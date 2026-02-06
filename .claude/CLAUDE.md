# AI Testing Resource - Deployment Guide

## Overview

This Flask application demonstrates AI evaluations in the testing pyramid. It deploys to AWS ECS Fargate with the following architecture:

**Production Stack:**
- **Container**: Flask app in Docker on ECS Fargate (0.25 vCPU, 512MB RAM)
- **Database**: RDS PostgreSQL (db.t4g.micro, 20GB storage) in private subnet
- **Load Balancer**: Application Load Balancer with HTTPS termination
- **API Gateway**: HTTP API with VPC Link to ALB
- **Registry**: ECR for Docker images
- **Secrets**: AWS Secrets Manager for API keys and DB credentials
- **Logs**: CloudWatch Logs for container output

**Integration**: Deployed at `https://portfolio.cookinupideas.com/ai-evals/` via CloudFront routing from the proto-portal-showcase-hub portfolio.

## Proxy Configuration

When deploying with a proxy, the application code must account for the proxy path.

Since this app is deployed at `/ai-evals/`, all routes are adjusted by setting the `APPLICATION_ROOT` environment variable to `/ai-evals/`.

This is configured in:
- ECS task definition: `APPLICATION_ROOT=/ai-evals` environment variable
- Terraform: `terraform/modules/ecs/main.tf` sets this in container definition

## Prerequisites

### Local Development
- **AWS CLI**: Installed and configured with credentials in `~/.aws/credentials`
- **Docker**: Docker daemon running locally
- **Terraform**: v1.0+ installed
- **jq**: JSON processor for deployment scripts
- **Git**: For commit-based image tagging
- **Anthropic API Key**: Required for Claude API access

### CI/CD (GitHub Actions)
- **AWS OIDC**: Role `arn:aws:iam::671388079324:role/github-actions-terraform-bootstrap`
- **GitHub Secrets**: `ANTHROPIC_API_KEY`, `TSR_API_TOKEN`, `TSR_API_URL`

## Deployment Process

### Step 1: Deploy Infrastructure (One-Time)

```bash
cd terraform/

# Initialize Terraform with S3 backend
terraform init

# Set required variables
export TF_VAR_anthropic_api_key="$ANTHROPIC_API_KEY"

# Plan infrastructure changes
terraform plan -out=tfplan.plan

# Review plan carefully, then apply
terraform apply tfplan.plan

# Capture important outputs
terraform output -raw alb_dns_name  # For portfolio integration
terraform output -raw api_gateway_domain  # Alternative origin
terraform output ecr_repository_url
```

**What this creates:**
- VPC with public/private subnets across 2 AZs
- Security groups for ALB, ECS, and RDS
- RDS PostgreSQL database with automatic backups
- ECS Fargate cluster and empty service
- ECR repository for Docker images
- Application Load Balancer with HTTPS
- API Gateway with VPC Link
- Secrets Manager entries for credentials

### Step 2: Deploy Application (Repeatable)

```bash
cd ai-testing-resource/

# Ensure .env file has ANTHROPIC_API_KEY
cp .env.example .env
# Edit .env and add your key

# Run deployment script
./scripts/deploy.sh
```

**What this does:**
1. Authenticates with ECR
2. Builds Docker image from `Dockerfile`
3. Tags image with git commit SHA and `latest`
4. Pushes both tags to ECR
5. Fetches current ECS task definition
6. Updates task definition with new image
7. Registers new task definition revision
8. Updates ECS service with new revision
9. Waits for service to stabilize (healthy tasks)

**Environment Variables (Set in Terraform):**
- `ANTHROPIC_API_KEY` - From Secrets Manager
- `TSR_DATABASE_URL` - RDS connection string from Secrets Manager
- `APPLICATION_ROOT` - `/ai-evals` for proxy routing
- `SECRET_KEY` - Generated Flask session secret
- `FLASK_HOST` - `0.0.0.0` (bind to all interfaces in container)
- `FLASK_PORT` - `5000` (container port)
- `CHROMA_PATH` - `/app/chroma_db` (persistent volume)
- `MONITORING_ENABLED` - `True`
- `TRACE_RETENTION_HOURS` - `24`

### Step 3: Verify Deployment

```bash
./scripts/verify-deployment.sh
```

**Checks performed:**
1. Health endpoint: `GET /health` returns `{"status": "healthy"}`
2. Root page: `GET /` returns 200 (redirects to `/ask`)
3. Ask page: `GET /ask` renders correctly
4. Governance dashboard: `GET /governance/dashboard` loads

**Manual verification:**
- Visit `https://portfolio.cookinupideas.com/ai-evals/`
- Check CloudWatch logs: `aws logs tail /ecs/ai-testing-resource-prod --follow`
- Verify ECS service health: `aws ecs describe-services --cluster ai-testing-resource-prod --services ai-testing-resource-prod`

## Deployment Scripts

### scripts/deploy.sh

**Purpose**: Build, push, and deploy Docker image to ECS.

**Configuration** (environment variables):
- `AWS_REGION` - Default: `us-east-1`
- `IMAGE_TAG` - Default: `$(git rev-parse --short HEAD)`

**Steps**:
1. ECR login via AWS CLI
2. Docker build with tag `671388079324.dkr.ecr.us-east-1.amazonaws.com/ai-testing-resource-prod:TAG`
3. Push with both commit SHA tag and `latest` tag
4. Fetch current task definition JSON
5. Update image field with new tag using `jq`
6. Register new task definition revision
7. Update ECS service to use new revision
8. Wait for service stability (all tasks healthy)

### scripts/verify-deployment.sh

**Purpose**: Smoke test deployed application endpoints.

**Configuration**:
- `PORTFOLIO_URL` - Default: `https://portfolio.cookinupideas.com`
- `APP_URL` - Default: `https://portfolio.cookinupideas.com/ai-evals`

**Checks**:
- `/health` endpoint returns JSON with `"healthy"`
- `/` returns HTTP 200
- `/ask` returns HTTP 200
- `/governance/dashboard` returns HTTP 200

## Integration with Portfolio

The AI Testing Resource is integrated into the proto-portal-showcase-hub portfolio at `https://portfolio.cookinupideas.com/ai-evals/`.

**CloudFront Configuration** (in portfolio repo):
- CloudFront distribution has two origins:
  1. **S3 origin**: Portfolio static site (default behavior)
  2. **ALB origin**: AI Testing Resource (path pattern `/ai-evals/*`)

**Portfolio Terraform Variable**:
```bash
# In proto-portal-showcase-hub/terraform/
terraform apply -var="ai_evals_alb_domain=<ALB_DNS_NAME>"
```

Get the ALB DNS name from AI Testing Resource Terraform output:
```bash
cd ai-evals-in-context/terraform/
terraform output -raw alb_dns_name
# Example: ai-testing-resource-prod-123456789.us-east-1.elb.amazonaws.com
```

**Alternative**: Use API Gateway domain for CloudFront origin (provides additional caching and throttling controls):
```bash
terraform output -raw api_gateway_domain
```

## Terraform Module Structure

```
terraform/
├── main.tf              # Composition of all modules
├── variables.tf         # Input variables
├── outputs.tf           # Outputs for integration
├── backend.tf           # S3 backend configuration
├── providers.tf         # AWS provider config
└── modules/
    ├── networking/      # VPC, subnets, security groups
    ├── database/        # RDS PostgreSQL + Secrets Manager
    ├── ecs/             # ECR, Fargate cluster, task def, service
    ├── alb/             # Application Load Balancer + HTTPS
    └── api_gateway/     # HTTP API + VPC Link
```

**State Management**:
- Backend: S3 bucket `ai-evals-terraform-state`
- Locking: DynamoDB table `ai-evals-terraform-locks`
- Region: `us-east-1`

## Required Terraform Variables

**Must be provided:**
- `anthropic_api_key` - Pass via `export TF_VAR_anthropic_api_key="sk-ant-..."`

**Optional (have defaults):**
- `aws_region` - Default: `us-east-1`
- `environment` - Default: `prod`
- `app_name` - Default: `ai-testing-resource`
- `domain_name` - Default: `portfolio.cookinupideas.com`
- `container_cpu` - Default: `256` (0.25 vCPU)
- `container_memory` - Default: `512` MB
- `db_instance_class` - Default: `db.t4g.micro`
- `db_allocated_storage` - Default: `20` GB

See `terraform/variables.tf` for complete list.

## Environment Variables Reference

### Production (ECS Task Definition)

Set in `terraform/modules/ecs/main.tf`:

| Variable | Value | Source |
|----------|-------|--------|
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Secrets Manager |
| `TSR_DATABASE_URL` | `postgresql://user:pass@host/db` | Secrets Manager |
| `APPLICATION_ROOT` | `/ai-evals` | Hardcoded (proxy path) |
| `SECRET_KEY` | Random 32-byte hex | Generated by Terraform |
| `FLASK_HOST` | `0.0.0.0` | Hardcoded |
| `FLASK_PORT` | `5000` | Hardcoded |
| `CHROMA_PATH` | `/app/chroma_db` | Hardcoded |
| `MONITORING_ENABLED` | `True` | Hardcoded |
| `TRACE_RETENTION_HOURS` | `24` | Hardcoded |

### CI/CD (GitHub Actions)

Set in GitHub repository secrets:

| Variable | Purpose |
|----------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for tests |
| `TSR_API_TOKEN` | Authentication for uploading TSRs |
| `TSR_API_URL` | API endpoint for TSR uploads |

**OIDC Role**: `arn:aws:iam::671388079324:role/github-actions-terraform-bootstrap`

## Cost Breakdown

**Monthly Estimate**: ~$19/month

| Service | Configuration | Cost |
|---------|--------------|------|
| ECS Fargate | 0.25 vCPU, 512MB, Spot | ~$3/month |
| RDS PostgreSQL | db.t4g.micro, 20GB, Multi-AZ disabled | ~$15/month |
| ALB | 1 ALB, low traffic | ~$16/month* |
| API Gateway | HTTP API, <1M requests | ~$0.01/month |
| ECR | <1GB storage | ~$0.50/month |
| Secrets Manager | 2 secrets | ~$0.40/month |
| CloudWatch Logs | <1GB/month | ~$0.50/month |

*Note: ALB cost may be shared if portfolio uses same ALB, reducing total cost.

## Troubleshooting

### Common Issues

**1. Proxy Routing Errors (404 or incorrect redirects)**
- **Symptom**: Pages return 404 or redirect to wrong URLs
- **Cause**: Missing `APPLICATION_ROOT=/ai-evals` environment variable
- **Fix**: Verify ECS task definition includes `APPLICATION_ROOT` variable
  ```bash
  aws ecs describe-task-definition --task-definition ai-testing-resource-prod \
    --query 'taskDefinition.containerDefinitions[0].environment'
  ```

**2. Health Check Failures**
- **Symptom**: ECS tasks marked unhealthy and continuously restart
- **Cause**: ALB health check path incorrect or app not responding on `:5000`
- **Fix**: Check ALB target group health check configuration
  ```bash
  aws elbv2 describe-target-health --target-group-arn <TG_ARN>
  ```
- Verify app listens on `FLASK_HOST=0.0.0.0` and `FLASK_PORT=5000`

**3. Database Connection Failures**
- **Symptom**: 500 errors, logs show database connection errors
- **Cause**: Security group rules or incorrect connection string
- **Fix**:
  - Verify ECS security group allows outbound to RDS security group on port 5432
  - Check `TSR_DATABASE_URL` in Secrets Manager matches RDS endpoint
  - Test connection from ECS task:
    ```bash
    aws ecs execute-command --cluster ai-testing-resource-prod \
      --task <TASK_ID> --container api --interactive --command "/bin/bash"
    ```

**4. Secrets Not Available**
- **Symptom**: App crashes with missing `ANTHROPIC_API_KEY` or database URL
- **Cause**: ECS task execution role lacks Secrets Manager permissions
- **Fix**: Verify IAM role has `secretsmanager:GetSecretValue` permission
  ```bash
  aws iam get-role-policy --role-name ecsTaskExecutionRole --policy-name SecretsManagerAccess
  ```

**5. Docker Build Failures**
- **Symptom**: `docker build` fails during deployment
- **Cause**: Missing dependencies, invalid Dockerfile, or build context issues
- **Fix**: Test build locally first:
  ```bash
  cd ai-testing-resource/
  docker build -t test:local .
  docker run -p 5000:5000 --env-file .env test:local
  ```

**6. Service Won't Stabilize**
- **Symptom**: `aws ecs wait services-stable` times out
- **Cause**: Tasks crash immediately after start, failing health checks
- **Fix**: Check CloudWatch logs for startup errors:
  ```bash
  aws logs tail /ecs/ai-testing-resource-prod --follow
  ```

## Use Scripts for Deployment

Use `scripts/deploy.sh` and `scripts/verify-deployment.sh` for both local and CI/CD deployments.

These scripts ensure consistency and reduce manual errors.

## Terraform Variable Syntax

Use `TF_VAR_` prefix for passing variables to Terraform:

```bash
export TF_VAR_anthropic_api_key="$ANTHROPIC_API_KEY"
terraform plan -out=tfplan.plan
terraform apply tfplan.plan
```

This approach:
- Keeps secrets out of command history
- Works consistently across local and CI/CD
- Avoids `-var` flag clutter

## AWS Credentials

- **Local**: Credentials in `~/.aws/credentials` with default profile
- **CI/CD**: GitHub Actions OIDC flow with role assumption

**CI/CD Role ARN**: `arn:aws:iam::671388079324:role/github-actions-terraform-bootstrap`

This role has permissions for:
- Terraform state access (S3 + DynamoDB)
- ECS, ECR, RDS, ALB, API Gateway management
- Secrets Manager read/write
- CloudWatch Logs write

