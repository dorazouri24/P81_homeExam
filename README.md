#Description
we created a Docker image that runs a Python script that times the response of a website.
The Python script is pulled from an S3 bucket, and the S3 key is provided as an environment variable. 
We also wrote a Bash script that validates the S3 key and checks if the S3 object is a Python script.
Finally, we added a command to the Dockerfile to run a start-up script that runs the Bash script and the Python script.

#Prerequisites

Docker installed on your system
AWS CLI installed on your system
AWS credentials configured on your system with permissions to create and push Docker images to ECR and access S3

#to Run the test in Terminal
#please provide access-Key & secret-key didn't want to put the hard coded 
python runTest.py --access-key Access-Key --secret-key Secret-Key
