#!/bin/bash
# Set variables
aws_region=us-east-1
aws_s3_key=$AWS_S3_KEY
aws_s3_bucket_name="p81-performance-test-scenarios/scripts/"
ECR_REGISTRY="369131898292.dkr.ecr.us-east-1.amazonaws.com"
ECR_REPOSITORY="p81-performance-test-repo"
DOCKER_IMAGE_NAME="p81-performance-test-image"

# local file path
local_file_path="main.py"

# download the file from S3
aws s3 cp "${aws_s3_key}" "${local_file_path}" 2>/dev/null

# Check if the download was successful
if [ "${local_file_path##*.}" = "py" ]; then
  python "${local_file_path}"
  echo "Python file run Successfully."
else
  echo "Error: Downloaded file is not a Python file."
  exit 1
fi
if [ -z "$AWS_S3_KEY" ]; then
  echo "AWS_S3_KEY environment variable is not set."
  exit 1
else
  echo "AWS_S3_KEY exists"
fi

# Exit the container
exit
