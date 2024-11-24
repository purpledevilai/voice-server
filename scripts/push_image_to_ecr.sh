#!/bin/bash

# Set variables
image_name="burrowai-property-estimator"
account_id="593793035725"
profile="burrowai"
aws_region="ap-southeast-2"
build_image=false

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --build) build_image=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Build the Docker image if --build is passed
if [ "$build_image" = true ]; then
    echo "Building the Docker image..."
    docker build --no-cache -t $image_name .
else
    echo "Skipping Docker image build."
fi

# Authenticate Docker to ECR
aws ecr get-login-password --region $aws_region --profile $profile | docker login --username AWS --password-stdin $account_id.dkr.ecr.$aws_region.amazonaws.com

# Check if the repository exists, and create it if it doesn't
aws ecr describe-repositories --repository-names $image_name --region $aws_region --profile $profile > /dev/null 2>&1

# $? holds the exit code of the last command
if [ $? -ne 0 ]; then
    echo "Repository $image_name does not exist. Creating..."
    aws ecr create-repository --repository-name $image_name --region $aws_region --profile $profile
else
    echo "Repository $image_name already exists."
fi

# Tag the Docker image
docker tag $image_name:latest $account_id.dkr.ecr.$aws_region.amazonaws.com/$image_name:latest

# Push the Docker image to ECR
docker push $account_id.dkr.ecr.$aws_region.amazonaws.com/$image_name:latest
