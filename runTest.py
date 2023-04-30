import subprocess
import argparse
import docker

parser = argparse.ArgumentParser()
parser.add_argument('--access-key', help='AWS access key ID')
parser.add_argument('--secret-key', help='AWS secret access key')
args = parser.parse_args()
if not args.access_key or not args.secret_key:
    print('Error: both --access-key and --secret-key arguments are required')
    exit()

# Set AWS configuration
subprocess.run(['aws', 'configure', 'set', 'aws_access_key_id', args.access_key])
subprocess.run(['aws', 'configure', 'set', 'aws_secret_access_key', args.secret_key])
subprocess.run(['aws', 'configure', 'set', 'default.region', 'us-east-1'])
subprocess.run(['aws', 'configure', 'set', 'default.output', 'json'])

# Upload script to S3
subprocess.run(['aws', 's3', 'cp', 'main.py', 's3://p81-performance-test-scenarios/scripts/'])

# Build and push Docker image to ECR

# Create a Docker client instance
client = docker.from_env()

# Build the Docker image
image, build_logs = client.images.build(
    path='.',
    tag='p81-performance-test-image',
    labels={
        'Name': 'DorAzouri',
        'Owner': 'Liad',
        'Department': 'Automation',
        'Temp': 'True'
    }
)
image.tag('369131898292.dkr.ecr.us-east-1.amazonaws.com/p81-performance-test-repo:latest')
client.images.pull('369131898292.dkr.ecr.us-east-1.amazonaws.com/p81-performance-test-repo:latest')
client.images.push('369131898292.dkr.ecr.us-east-1.amazonaws.com/p81-performance-test-repo:latest')
container = client.containers.run(
    '369131898292.dkr.ecr.us-east-1.amazonaws.com/p81-performance-test-repo:latest',
    remove=True
)
decoded_response = container.decode('utf-8')
print(decoded_response.replace('b\'', '').replace('\\n', ''))

# To Run Q 2,3
# subprocess.run(['python', 'AWSCloudSpot.py', '--access-key', args.access_key, '--secret-key', args.secret_key])
