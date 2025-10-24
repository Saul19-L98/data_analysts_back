#!/usr/bin/env pwsh
# AWS ECR Deployment Script for Data Analyst Backend
# This script builds and pushes the Docker image to AWS ECR

$ErrorActionPreference = "Stop"

# Configuration
$AWS_REGION = "us-east-2"
$ECR_REPOSITORY = "data_analystt_back"
$IMAGE_TAG = if ($args[0]) { $args[0] } else { "latest" }
$AWS_PROFILE = "connect_dev_user"

# Set AWS profile
$env:AWS_PROFILE = $AWS_PROFILE
Write-Host "🔐 Using AWS Profile: $AWS_PROFILE" -ForegroundColor Cyan

Write-Host "🚀 Building Data Analyst Docker Image for AWS ECR" -ForegroundColor Green

# Get AWS account ID
Write-Host "📋 Getting AWS account ID..." -ForegroundColor Yellow
try {
    $AWS_ACCOUNT_ID = (aws sts get-caller-identity --profile $AWS_PROFILE --query Account --output text)
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to get AWS account ID. Check your AWS credentials and profile."
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    exit 1
}

$ECR_REGISTRY = "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

Write-Host "✅ AWS Account ID: $AWS_ACCOUNT_ID" -ForegroundColor Green
Write-Host "📍 ECR Registry: $ECR_REGISTRY" -ForegroundColor Green

# Check if ECR repository exists, create if it doesn't
Write-Host "🔍 Checking if ECR repository exists..." -ForegroundColor Yellow
$repoExists = $true
try {
    aws ecr describe-repositories `
        --profile $AWS_PROFILE `
        --region $AWS_REGION `
        --repository-names $ECR_REPOSITORY `
        2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        $repoExists = $false
    }
} catch {
    $repoExists = $false
}

if (-not $repoExists) {
    Write-Host "📦 Creating ECR repository: $ECR_REPOSITORY..." -ForegroundColor Yellow
    aws ecr create-repository `
        --profile $AWS_PROFILE `
        --region $AWS_REGION `
        --repository-name $ECR_REPOSITORY `
        --image-scanning-configuration scanOnPush=true `
        --encryption-configuration encryptionType=AES256
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to create ECR repository" -ForegroundColor Red
        exit 1
    }
    Write-Host "✅ Repository created successfully" -ForegroundColor Green
} else {
    Write-Host "✅ Repository already exists" -ForegroundColor Green
}

# Build Docker image
Write-Host "📦 Building Docker image..." -ForegroundColor Yellow
docker build -t "$ECR_REPOSITORY`:$IMAGE_TAG" .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker build failed" -ForegroundColor Red
    exit 1
}

# Tag image for ECR
Write-Host "🏷️ Tagging image for ECR..." -ForegroundColor Yellow
docker tag "$ECR_REPOSITORY`:$IMAGE_TAG" "$ECR_REGISTRY/$ECR_REPOSITORY`:$IMAGE_TAG"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker tag failed" -ForegroundColor Red
    exit 1
}

# Login to ECR
Write-Host "🔐 Logging into ECR..." -ForegroundColor Yellow
$loginPassword = aws ecr get-login-password --profile $AWS_PROFILE --region $AWS_REGION
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Failed to get ECR login password" -ForegroundColor Red
    exit 1
}

$loginPassword | docker login --username AWS --password-stdin $ECR_REGISTRY
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker login to ECR failed" -ForegroundColor Red
    exit 1
}

# Push image to ECR
Write-Host "⬆️ Pushing image to ECR..." -ForegroundColor Yellow
docker push "$ECR_REGISTRY/$ECR_REPOSITORY`:$IMAGE_TAG"
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker push failed" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ ==========================================" -ForegroundColor Green
Write-Host "✅ Image successfully pushed to ECR!" -ForegroundColor Green
Write-Host "✅ ==========================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Image URI: $ECR_REGISTRY/$ECR_REPOSITORY`:$IMAGE_TAG" -ForegroundColor Cyan
Write-Host ""
Write-Host "🚀 Next steps:" -ForegroundColor Yellow
Write-Host "   1. Update ECS task definition with this image URI"
Write-Host "   2. Deploy to ECS using AWS Console or CLI"
Write-Host ""
Write-Host "📝 Copy this image URI for your task definition:" -ForegroundColor Cyan
Write-Host "   $ECR_REGISTRY/$ECR_REPOSITORY`:$IMAGE_TAG" -ForegroundColor White
Write-Host ""
