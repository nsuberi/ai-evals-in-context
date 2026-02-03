#!/bin/bash
set -e

# Configuration
AWS_REGION="${AWS_REGION:-us-east-1}"
ECR_REGISTRY="671388079324.dkr.ecr.${AWS_REGION}.amazonaws.com"
ECR_REPOSITORY="ai-testing-resource-prod"
ECS_CLUSTER="ai-testing-resource-prod"
ECS_SERVICE="ai-testing-resource-prod"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"

echo "=== Deploying to AWS ECS ==="
echo "Image tag: $IMAGE_TAG"
echo "Region: $AWS_REGION"

# Step 1: Login to ECR
echo "Logging into ECR..."
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_REGISTRY

# Step 2: Build Docker image
echo "Building Docker image..."
docker build -t $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG .
docker tag $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPOSITORY:latest

# Step 3: Push to ECR
echo "Pushing to ECR..."
docker push $ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG
docker push $ECR_REGISTRY/$ECR_REPOSITORY:latest

# Step 4: Update ECS task definition
echo "Fetching current task definition..."
TASK_DEF=$(aws ecs describe-task-definition \
    --task-definition $ECS_SERVICE \
    --region $AWS_REGION \
    --query 'taskDefinition' \
    --output json)

# Update image in task definition
NEW_TASK_DEF=$(echo $TASK_DEF | jq --arg IMG "$ECR_REGISTRY/$ECR_REPOSITORY:$IMAGE_TAG" \
    '.containerDefinitions[0].image = $IMG |
     del(.taskDefinitionArn, .revision, .status, .requiresAttributes, .compatibilities, .registeredAt, .registeredBy)')

# Register new task definition
echo "Registering new task definition..."
NEW_TASK_ARN=$(aws ecs register-task-definition \
    --region $AWS_REGION \
    --cli-input-json "$NEW_TASK_DEF" \
    --query 'taskDefinition.taskDefinitionArn' \
    --output text)

echo "New task definition: $NEW_TASK_ARN"

# Step 5: Update ECS service
echo "Updating ECS service..."
aws ecs update-service \
    --region $AWS_REGION \
    --cluster $ECS_CLUSTER \
    --service $ECS_SERVICE \
    --task-definition $NEW_TASK_ARN \
    --force-new-deployment

# Step 6: Wait for deployment
echo "Waiting for service stability..."
aws ecs wait services-stable \
    --region $AWS_REGION \
    --cluster $ECS_CLUSTER \
    --services $ECS_SERVICE

echo "=== Deployment complete! ==="
echo "Service URL: https://portfolio.cookinupideas.com/ai-evals/"
