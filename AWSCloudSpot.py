import argparse
import base64
import json
import subprocess
import boto3
import paramiko
import time

# AWS credentials
parser = argparse.ArgumentParser()
parser.add_argument('--access-key', help='AWS access key ID')
parser.add_argument('--secret-key', help='AWS secret access key')
args = parser.parse_args()
if not args.access_key or not args.secret_key:
    print('Error: both --access-key and --secret-key arguments are required')
    exit()

# EC2 and CloudWatch clients objects
ec2_client = boto3.client('ec2', aws_access_key_id=args.access_key, aws_secret_access_key=args.secret_key)
cloudwatch_client = boto3.client('logs', aws_access_key_id=args.access_key, aws_secret_access_key=args.secret_key)
ssh_client = paramiko.SSHClient()
ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

# Configuration
region = 'us-west-2'
availability_zones = ['us-east-1a', 'us-east-1b', 'us-east-1c']
instance_type = 't2.micro'
ami_id = 'ami-01b20f5ea962e3fe7'
user_data = '''#!/bin/bash
sudo yum update -y
sudo yum install -y docker
sudo service docker start
sudo usermod -aG docker ec2-user
sudo yum install -y python3
'''
encoded_user_data = base64.b64encode(user_data.encode()).decode()
spot_price = '0.01'
instance_count = 3  # change it for X instances
instance_duration = 10
security_group_id = 'sg-02aa3206f109ba2b8'
subnet_id = 'subnet-016cdceb1fa53b884'
docker_image = 'p81-performance-test-image:latest'
container_name = 'upbeat_curie'
container_port = 80
log_group_name = 'log-group'
log_stream_name = 'log-stream'

# Step 1: Launch Spot instances
print(f'Launching {instance_count} Spot instances of type {instance_type}...')
response = ec2_client.request_spot_instances(
    InstanceCount=instance_count,
    LaunchSpecification={
        'ImageId': ami_id,
        'InstanceType': instance_type,
        'KeyName': 'my-key-pair',
        'UserData': encoded_user_data,
        'SecurityGroupIds': [security_group_id],
        'SubnetId': subnet_id
    },
    SpotPrice=spot_price,
    Type='one-time',
    ValidUntil=int(time.time()) + instance_duration * 60,
    AvailabilityZoneGroup=','.join(availability_zones)
)

# Wait for Spot instances to be launched
spot_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
print(f'Waiting for Spot request {spot_request_id} to be fulfilled...')
waiter = ec2_client.get_waiter('spot_instance_request_fulfilled')
waiter.wait(SpotInstanceRequestIds=[spot_request_id])

# Get information about the launched instances
response = ec2_client.describe_spot_instance_requests(SpotInstanceRequestIds=[spot_request_id])
instance_ids = [r['InstanceId'] for r in response['SpotInstanceRequests']]

# Wait for the instances to be running
print(f'Waiting for instances {instance_ids} to be running...')
waiter = ec2_client.get_waiter('instance_running')
waiter.wait(InstanceIds=instance_ids)

# Get public DNS names of the instances
response = ec2_client.describe_instances(InstanceIds=instance_ids)
public_dns_names = [i['PublicDnsName'] for r in response['Reservations'] for i in r['Instances']]

# SSH into the instances and run Docker containers
# for dns_name in public_dns_names:
#     print(f'SSH into {dns_name}...')
#     ssh_client.connect(hostname=dns_name, username='ec2-user', key_filename='my-key-pair.pem')
#     cmd = f'sudo docker run -d --name {container_name} -p {container_port}:80 {docker_image}'
#     stdin, stdout, stderr = ssh_client.exec_command(cmd)
#     print(stdout.read().decode())
#     print(stderr.read().decode())
# ssh_client.close()

# Wait for the containers to finish or timeout
end_time = time.time() + instance_duration * 60
while True:
    response = cloudwatch_client.filter_log_events(
        logGroupName=log_group_name,
        logStreamNames=[log_stream_name],
        filterPattern='Error'
    )
    if response['events']:
        print(f'Error in container logs: {response["events"]}')
        break
    elif time.time() > end_time:
        print('Timeout reached, terminating instances...')
        ec2_client.terminate_instances(InstanceIds=instance_ids)
        break
    else:
        time.sleep(10)

# Q3 Define the names of the resources to be created
dashboard_name = 'DorAzouriDashboard'
widget_name = 'MyWidget'

# Trigger the Python script to create the resources and capture its output
output = subprocess.check_output(['python3', 'main.py'])

# Define the metrics to be displayed in the dashboard
metric_instances_created = {
    'id': 'm1',
    'label': 'Instances Created',
    'metric': 'EC2/SpotInstanceRequests',
    'stat': 'Sum',
    'period': 300,
    'region': region,
    'dimensions': [{'Name': 'RequestType', 'Value': 'one-time'}, {'Name': 'State', 'Value': 'active'}]
}

metric_containers_created = {
    'id': 'm2',
    'label': 'Containers Created',
    'metric': 'DockerHub/ContainersCreated',
    'stat': 'Sum',
    'period': 300,
    'region': region,
}

metric_request_time = {
    'id': 'm3',
    'label': 'Request Time',
    'metric': 'DockerHub/RequestTime',
    'stat': 'Average',
    'period': 300,
    'region': region,
}

# Parse the output to extract the instance count and the CloudWatch dashboard URL
instance_count = None
dashboard_url = None
for line in output.decode().split('\n'):
    if line.startswith('Created'):
        instance_count = int(line.split()[-1])
    elif line.startswith('Dashboard URL:'):
        dashboard_url = line.split()[-1]

# Create the CloudWatch dashboard
cloudwatch_client = boto3.client('cloudwatch')
response = cloudwatch_client.put_dashboard(
    DashboardName=dashboard_name,
    DashboardBody=json.dumps({
        'widgets': [{
            'type': 'metric',
            'x': 0,
            'y': 0,
            'width': 12,
            'height': 6,
            'properties': {
                'metrics': [metric_instances_created, metric_containers_created, metric_request_time],
                'view': 'timeSeries',
                'stacked': False,
                'region': region,
                'title': 'My Dashboard',
                'period': 300,
            }
        }]
    })
)

# Print a message with the instance count and the CloudWatch dashboard URL
print(f'Created {instance_count} instances')
print(f'Dashboard URL: {dashboard_url}')
