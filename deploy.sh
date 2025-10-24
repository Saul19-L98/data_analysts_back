#!/bin/bash

# AWS ECR Deployment Script for TotalFOB Export Scraper
# This script builds and pushes the Docker image to AWS ECR

set -e

# Configuration
AWS_REGION="us-east-2"
ECR_REPOSITORY="data_analystt_back"
IMAGE_TAG="latest"  # Default to latest, can be overridden with first argument
AWS_PROFILE="connect_dev_user"

# Set AWS profile
export AWS_PROFILE="$AWS_PROFILE"
echo "🔐 Using AWS Profile: $AWS_PROFILE"

echo "🚀 Building Data Analyst Docker Image for AWS ECR"

# Get AWS account ID
echo "📋 Getting AWS account ID..."
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --profile ${AWS_PROFILE} --query Account --output text)
ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "✅ AWS Account ID: $AWS_ACCOUNT_ID"
echo "📍 ECR Registry: $ECR_REGISTRY"

# Check if ECR repository exists, create if it doesn't
echo "🔍 Checking if ECR repository exists..."
if ! aws ecr describe-repositories --profile ${AWS_PROFILE} --region ${AWS_REGION} --repository-names ${ECR_REPOSITORY} >/dev/null 2>&1; then
    echo "📦 Creating ECR repository: ${ECR_REPOSITORY}..."
    aws ecr create-repository \
        --profile ${AWS_PROFILE} \
        --region ${AWS_REGION} \
        --repository-name ${ECR_REPOSITORY} \
        --image-scanning-configuration scanOnPush=true \
        --encryption-configuration encryptionType=AES256
    echo "✅ Repository created successfully"
else
    echo "✅ Repository already exists"
fi

echo "📦 Building Docker image..."
docker build -t ${ECR_REPOSITORY}:${IMAGE_TAG} .

echo "🏷️ Tagging image for ECR..."
docker tag ${ECR_REPOSITORY}:${IMAGE_TAG} ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}

echo "🔐 Logging into ECR..."
aws ecr get-login-password --profile ${AWS_PROFILE} --region ${AWS_REGION} | \
    docker login --username AWS --password-stdin ${ECR_REGISTRY}

echo "⬆️ Pushing image to ECR..."
docker push ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}

echo ""
echo "✅ =========================================="
echo "✅ Image successfully pushed to ECR!"
echo "✅ =========================================="
echo ""
echo "📋 Image URI: ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
echo ""
echo "🚀 Next steps:"
echo "   1. Update ECS task definition with this image URI"
echo "   2. Deploy to ECS using AWS Console or CLI"
echo ""
echo "📝 Copy this image URI for your task definition:"
echo "   ${ECR_REGISTRY}/${ECR_REPOSITORY}:${IMAGE_TAG}"
echo ""
