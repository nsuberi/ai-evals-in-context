# Terraform Infrastructure Documentation

This directory contains Terraform configurations for deploying the AI Testing Resource application to AWS.

## Overview

The infrastructure uses a modular approach to deploy a production-ready Flask application on AWS ECS Fargate with managed PostgreSQL database, application load balancing, and secure secrets management.

**Architecture Components:**
- **Networking**: VPC with public/private subnets across multiple availability zones
- **Compute**: ECS Fargate cluster with Spot instances for cost optimization
- **Database**: RDS PostgreSQL in private subnet with automated backups
- **Load Balancing**: Application Load Balancer with HTTPS termination
- **API Gateway**: HTTP API with VPC Link for CloudFront integration
- **Container Registry**: ECR for Docker images
- **Secrets**: AWS Secrets Manager for credentials
- **Monitoring**: CloudWatch Logs for container output

**Deployment URL**: `https://portfolio.cookinupideas.com/ai-evals/`

## Architecture Diagram

```
Internet
    ↓
CloudFront (portfolio.cookinupideas.com)
    ↓ /ai-evals/*
Application Load Balancer (HTTPS)
    ↓
VPC Link (API Gateway) [Optional]
    ↓
ECS Fargate Tasks (Flask containers)
    ↓
Private Subnet
    ↓
RDS PostgreSQL

Supporting Services:
- ECR: Container images
- Secrets Manager: Credentials
- CloudWatch: Logs and metrics
```

## Module Structure

### networking/
**Purpose**: Creates VPC, subnets, and security groups.

**Resources**:
- VPC with CIDR `10.0.0.0/16`
- 2 public subnets (for ALB)
- 2 private subnets (for ECS and RDS)
- Internet Gateway for public subnet access
- NAT Gateway for private subnet outbound (optional)
- Security groups:
  - ALB: Allows inbound 80/443, outbound to ECS
  - ECS: Allows inbound from ALB on port 5000, outbound to RDS and internet
  - RDS: Allows inbound from ECS on port 5432

**Outputs**:
- `vpc_id`
- `public_subnet_ids`
- `private_subnet_ids`
- `alb_security_group_id`
- `ecs_security_group_id`
- `rds_security_group_id`

### database/
**Purpose**: Creates RDS PostgreSQL database with secrets management.

**Resources**:
- RDS PostgreSQL instance (db.t4g.micro, 20GB)
- DB subnet group across private subnets
- Random password generation for database
- Secrets Manager secrets:
  - `ai-testing-resource/anthropic-api-key`
  - `ai-testing-resource/database-credentials`
- DB parameter group (optional customization)
- Automated backups (7-day retention)

**Configuration**:
- Multi-AZ: Disabled (cost optimization)
- Storage type: gp3 (better performance/cost than gp2)
- Backup window: 03:00-04:00 UTC
- Maintenance window: Sun 04:00-05:00 UTC
- Deletion protection: Enabled

**Outputs**:
- `db_endpoint` - Connection hostname
- `db_port` - PostgreSQL port (5432)
- `db_name` - Database name
- `anthropic_api_key_arn` - Secret ARN
- `database_credentials_arn` - Secret ARN

### ecs/
**Purpose**: Creates container orchestration infrastructure.

**Resources**:
- ECR repository for Docker images
- ECS Fargate cluster
- ECS task definition:
  - CPU: 256 units (0.25 vCPU)
  - Memory: 512 MB
  - Container: Flask app on port 5000
  - Environment variables from Secrets Manager
  - CloudWatch Logs integration
- ECS service:
  - Desired count: 1
  - Capacity provider: FARGATE_SPOT (70% cost savings)
  - Health check grace period: 60s
  - Deployment circuit breaker enabled
- IAM roles:
  - Task execution role (pull images, read secrets, write logs)
  - Task role (application permissions)

**Task Definition Environment Variables**:
```json
[
  {
    "name": "ANTHROPIC_API_KEY",
    "valueFrom": "arn:aws:secretsmanager:...:secret:anthropic-api-key"
  },
  {
    "name": "TSR_DATABASE_URL",
    "valueFrom": "arn:aws:secretsmanager:...:secret:database-credentials"
  },
  {
    "name": "APPLICATION_ROOT",
    "value": "/ai-evals"
  },
  {
    "name": "FLASK_HOST",
    "value": "0.0.0.0"
  },
  {
    "name": "FLASK_PORT",
    "value": "5000"
  },
  {
    "name": "CHROMA_PATH",
    "value": "/app/chroma_db"
  },
  {
    "name": "MONITORING_ENABLED",
    "value": "True"
  },
  {
    "name": "TRACE_RETENTION_HOURS",
    "value": "24"
  }
]
```

**Outputs**:
- `cluster_name`
- `service_name`
- `task_definition_arn`
- `ecr_repository_url`
- `log_group_name`

### alb/
**Purpose**: Creates Application Load Balancer with HTTPS.

**Resources**:
- Application Load Balancer (internet-facing)
- Target group:
  - Protocol: HTTP
  - Port: 5000
  - Health check: `GET /health`
  - Health check interval: 30s
  - Healthy threshold: 2
  - Unhealthy threshold: 3
  - Timeout: 5s
- HTTPS listener (port 443):
  - SSL certificate: Reused from portfolio (*.cookinupideas.com)
  - SSL policy: ELBSecurityPolicy-TLS-1-2-2017-01
  - Default action: Forward to target group
- HTTP listener (port 80):
  - Redirects to HTTPS

**ACM Certificate**:
- ARN: `arn:aws:acm:us-east-1:671388079324:certificate/4240573d-1c6a-44ec-9eee-eedc5f4c9157`
- Domain: `*.cookinupideas.com`
- Shared with proto-portal-showcase-hub

**Outputs**:
- `alb_dns_name` - Use for CloudFront origin
- `alb_zone_id` - For Route 53 alias records
- `target_group_arn`

### api_gateway/
**Purpose**: Creates HTTP API with VPC Link for CloudFront integration.

**Resources**:
- HTTP API (not REST API - simpler and cheaper)
- VPC Link to ALB
- Default route: `ANY /{proxy+}` → ALB
- Stage: `$default` (auto-deploy)
- Throttling: 10,000 requests/second burst

**Why API Gateway?**
- Additional caching layer before ALB
- Request throttling and rate limiting
- CloudFront origin with managed AWS service
- Better integration with AWS WAF (optional)
- Simpler CloudFront origin configuration

**Outputs**:
- `api_endpoint` - Full API Gateway URL
- `api_domain` - Domain for CloudFront origin

## State Management

**Backend Configuration** (`backend.tf`):
```hcl
terraform {
  backend "s3" {
    bucket         = "ai-evals-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "ai-evals-terraform-locks"
    encrypt        = true
  }
}
```

**State Storage**:
- S3 bucket: `ai-evals-terraform-state` (versioned, encrypted)
- DynamoDB table: `ai-evals-terraform-locks` (for state locking)
- Region: `us-east-1`

**Prerequisites**: These resources must exist before running Terraform. Create manually or use the bootstrap script in `scripts/bootstrap-backend.sh`.

## Required Variables

These variables MUST be provided:

| Variable | Type | Description | How to Provide |
|----------|------|-------------|----------------|
| `anthropic_api_key` | string (sensitive) | Anthropic API key for Claude | `export TF_VAR_anthropic_api_key="sk-ant-..."` |

## Optional Variables (with defaults)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `aws_region` | string | `us-east-1` | AWS region for resources |
| `environment` | string | `prod` | Environment name |
| `app_name` | string | `ai-testing-resource` | Application name |
| `domain_name` | string | `portfolio.cookinupideas.com` | Domain name |
| `route53_zone_id` | string | `Z0990573XMA6PHFKL82S` | Route 53 zone ID |
| `container_cpu` | number | `256` | CPU units (256 = 0.25 vCPU) |
| `container_memory` | number | `512` | Memory in MB |
| `container_port` | number | `5000` | Container port |
| `db_instance_class` | string | `db.t4g.micro` | RDS instance type |
| `db_allocated_storage` | number | `20` | RDS storage in GB |
| `db_name` | string | `tsr_db` | Database name |
| `db_username` | string | `tsr_user` | Database username |
| `vpc_cidr` | string | `10.0.0.0/16` | VPC CIDR block |
| `availability_zones` | list(string) | `["us-east-1a", "us-east-1b"]` | AZs to use |
| `certificate_arn` | string | (portfolio cert) | ACM certificate ARN |

See `variables.tf` for complete variable definitions.

## Deployment Workflow

### Initial Setup (First Time)

```bash
# 1. Initialize Terraform
cd terraform/
terraform init

# 2. Create terraform.tfvars (optional, for non-default values)
cat > terraform.tfvars <<EOF
aws_region = "us-east-1"
environment = "prod"
app_name = "ai-testing-resource"
EOF

# 3. Set sensitive variables via environment
export TF_VAR_anthropic_api_key="$ANTHROPIC_API_KEY"

# 4. Validate configuration
terraform validate

# 5. Plan infrastructure
terraform plan -out=tfplan.plan

# 6. Review plan carefully
# Check resource counts, configurations, and costs

# 7. Apply infrastructure
terraform apply tfplan.plan

# 8. Save outputs
terraform output -json > outputs.json
terraform output -raw alb_dns_name > alb_domain.txt
terraform output -raw ecr_repository_url > ecr_url.txt
```

### Updates (Infrastructure Changes)

```bash
# 1. Make changes to .tf files

# 2. Format code
terraform fmt

# 3. Validate changes
terraform validate

# 4. Plan changes
export TF_VAR_anthropic_api_key="$ANTHROPIC_API_KEY"
terraform plan -out=tfplan.plan

# 5. Review changes carefully
# Look for resource replacements (dangerous!)

# 6. Apply changes
terraform apply tfplan.plan
```

### Viewing Current State

```bash
# List all resources
terraform state list

# Show specific resource
terraform state show module.ecs.aws_ecs_service.main

# View outputs
terraform output

# View sensitive output (e.g., database endpoint)
terraform output -raw rds_endpoint
```

### Destroying Infrastructure

```bash
# WARNING: This deletes all AWS resources!

# 1. Plan destruction
terraform plan -destroy -out=destroy.plan

# 2. Review what will be deleted

# 3. Destroy (irreversible!)
terraform apply destroy.plan
```

## Outputs Reference

After applying Terraform, these outputs are available:

| Output | Description | Use Case |
|--------|-------------|----------|
| `api_gateway_url` | API Gateway endpoint URL | Testing, CloudFront origin |
| `api_gateway_domain` | API Gateway domain | CloudFront origin configuration |
| `alb_dns_name` | ALB DNS name | CloudFront origin (direct ALB) |
| `alb_zone_id` | ALB hosted zone ID | Route 53 alias records |
| `ecr_repository_url` | ECR repository URL | Docker push target |
| `ecs_cluster_name` | ECS cluster name | Deployment scripts |
| `ecs_service_name` | ECS service name | Deployment scripts |
| `rds_endpoint` | RDS connection endpoint | Database access |
| `cloudwatch_log_group` | Log group name | Viewing logs |
| `vpc_id` | VPC ID | Network troubleshooting |

**Accessing outputs**:
```bash
# All outputs as JSON
terraform output -json

# Specific output (raw, no quotes)
terraform output -raw alb_dns_name

# Specific output (with quotes and type info)
terraform output alb_dns_name
```

## Integration with Portfolio

The portfolio (proto-portal-showcase-hub) CloudFront distribution needs the ALB domain to route `/ai-evals/*` traffic.

### Step 1: Get ALB Domain

```bash
cd ai-evals-in-context/terraform/
terraform output -raw alb_dns_name
# Example: ai-testing-resource-prod-123456789.us-east-1.elb.amazonaws.com
```

### Step 2: Configure Portfolio Terraform

```bash
cd proto-portal-showcase-hub/terraform/

# Pass ALB domain as variable
terraform apply -var="ai_evals_alb_domain=<ALB_DNS_NAME_FROM_STEP_1>"
```

This configures CloudFront to:
1. Route `https://portfolio.cookinupideas.com/ai-evals/*` to the ALB
2. Use HTTPS for origin communication
3. Forward all headers and query strings
4. Cache only static assets (CSS, JS, images)

### Alternative: API Gateway Origin

For additional caching and throttling, use API Gateway as CloudFront origin instead:

```bash
# Get API Gateway domain
terraform output -raw api_gateway_domain

# Pass to portfolio
cd proto-portal-showcase-hub/terraform/
terraform apply -var="ai_evals_origin_domain=<API_GATEWAY_DOMAIN>"
```

## Cost Breakdown

**Monthly cost estimate**: ~$19/month (with low traffic)

| Service | Configuration | Monthly Cost |
|---------|--------------|--------------|
| **ECS Fargate** | 0.25 vCPU, 512MB, Spot, 1 task, 730 hours | ~$3.00 |
| **RDS PostgreSQL** | db.t4g.micro, 20GB gp3, single-AZ | ~$15.00 |
| **ALB** | 1 ALB, 0.5 LCU average | ~$16.00 |
| **API Gateway** | HTTP API, <1M requests | ~$0.01 |
| **ECR** | <1GB image storage | ~$0.10 |
| **Secrets Manager** | 2 secrets | ~$0.80 |
| **CloudWatch Logs** | <1GB logs/month | ~$0.50 |
| **Data Transfer** | <1GB outbound | ~$0.09 |
| **NAT Gateway** | 0 if using public subnets | $0 or ~$32/month |
| **Total (without NAT)** | | **~$35.50/month** |
| **Total (with shared ALB)** | | **~$19.50/month** |

**Cost optimization strategies**:
1. **Fargate Spot**: 70% savings vs on-demand (configured)
2. **Shared ALB**: Portfolio and AI Evals share one ALB (~$16 saved)
3. **No NAT Gateway**: ECS in public subnet with public IP (configured)
4. **gp3 storage**: 20% cheaper than gp2 for RDS
5. **Single-AZ RDS**: No Multi-AZ for dev/demo (~50% DB cost saved)
6. **Minimal instance sizes**: db.t4g.micro, 0.25 vCPU

**Scaling costs**:
- Each additional ECS task: +$3/month
- Doubling RDS storage (20GB → 40GB): +$2/month
- High traffic (10M requests): +$10/month API Gateway

## Security Considerations

### Network Security
- RDS in private subnet (no public internet access)
- ECS security group only allows traffic from ALB
- RDS security group only allows traffic from ECS
- ALB security group allows 80/443 from internet

### Secrets Management
- API keys stored in Secrets Manager (encrypted at rest)
- Database password auto-generated and stored in Secrets Manager
- Secrets accessed via IAM roles (no hardcoded credentials)
- ECS task execution role has least-privilege access

### Transport Security
- HTTPS enforced on ALB (HTTP redirects to HTTPS)
- TLS 1.2+ only (ELBSecurityPolicy-TLS-1-2-2017-01)
- Secrets Manager API calls over HTTPS
- ECS → RDS communication within VPC (encrypted with SSL)

### IAM Roles
- **Task Execution Role**: Pull images, read secrets, write logs
- **Task Role**: Application-level permissions (currently minimal)
- Both follow least-privilege principle

### Monitoring
- CloudWatch Logs capture all container output
- ALB access logs available (currently disabled, enable if needed)
- CloudWatch Alarms for health check failures (optional)

## Troubleshooting

### Terraform Errors

**State Lock Error**:
```
Error: Error acquiring the state lock
```
**Cause**: Another Terraform operation is running, or previous run crashed.
**Fix**:
```bash
# Wait for other operation to finish, or force unlock (dangerous!)
terraform force-unlock <LOCK_ID>
```

**Provider Authentication Error**:
```
Error: error configuring Terraform AWS Provider: no valid credential sources
```
**Cause**: AWS credentials not configured.
**Fix**:
```bash
aws configure
# Or set environment variables
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
```

**Module Source Error**:
```
Error: Module not installed
```
**Cause**: Terraform modules not downloaded.
**Fix**:
```bash
terraform init
```

### Infrastructure Issues

**ECS Tasks Won't Start**:
- Check CloudWatch Logs: `aws logs tail /ecs/ai-testing-resource-prod --follow`
- Verify secrets exist in Secrets Manager
- Check IAM task execution role has `secretsmanager:GetSecretValue`
- Ensure ECR image exists and is accessible

**ALB Health Checks Fail**:
- Verify ECS tasks are running: `aws ecs describe-services --cluster ai-testing-resource-prod --services ai-testing-resource-prod`
- Check Flask app listens on `0.0.0.0:5000` not `127.0.0.1:5000`
- Test `/health` endpoint returns 200: `curl <ALB_DNS>/health`
- Review target group health: `aws elbv2 describe-target-health --target-group-arn <ARN>`

**Database Connection Fails**:
- Verify RDS security group allows traffic from ECS security group
- Check RDS endpoint in Secrets Manager matches actual RDS endpoint
- Ensure `TSR_DATABASE_URL` format is correct: `postgresql://user:pass@host:5432/dbname`
- Test connection from ECS task (if `nc` or `psql` available)

**Terraform Drift**:
- Resources manually modified in AWS console
- Fix: `terraform plan` will show drift, `terraform apply` to reconcile

### Accessing Resources

**View ECS Task Logs**:
```bash
aws logs tail /ecs/ai-testing-resource-prod --follow
```

**Execute Command in Running Task**:
```bash
# Enable execute command in ECS service first
aws ecs execute-command \
  --cluster ai-testing-resource-prod \
  --task <TASK_ID> \
  --container api \
  --interactive \
  --command "/bin/bash"
```

**Connect to RDS Database**:
```bash
# From within VPC (e.g., ECS task or bastion host)
psql "postgresql://tsr_user:<PASSWORD>@<RDS_ENDPOINT>:5432/tsr_db"
```

**View Secrets**:
```bash
# Anthropic API key
aws secretsmanager get-secret-value \
  --secret-id ai-testing-resource/anthropic-api-key \
  --query 'SecretString' --output text

# Database credentials
aws secretsmanager get-secret-value \
  --secret-id ai-testing-resource/database-credentials \
  --query 'SecretString' --output text
```

## Maintenance

### Updating Dependencies

**Terraform Provider Updates**:
```bash
# Check for updates
terraform init -upgrade

# Review changes
cat .terraform.lock.hcl

# Test
terraform plan
```

**Module Updates**:
- Modules are local (no remote dependencies)
- Update by modifying files in `modules/` directory
- Test in staging environment first

### Backup and Restore

**RDS Automated Backups**:
- Retention: 7 days
- Window: 03:00-04:00 UTC daily
- Restore via AWS console or CLI

**Manual RDS Snapshot**:
```bash
aws rds create-db-snapshot \
  --db-instance-identifier ai-testing-resource-prod \
  --db-snapshot-identifier manual-backup-$(date +%Y%m%d)
```

**Terraform State Backup**:
- Automatic versioning in S3
- Download backup: `aws s3 cp s3://ai-evals-terraform-state/prod/terraform.tfstate backup.tfstate`

### Disaster Recovery

**Complete Infrastructure Loss**:
1. Restore Terraform state from S3 backup
2. Run `terraform plan` to see drift
3. Manually recreate any missing backend resources (S3 bucket, DynamoDB table)
4. Run `terraform apply` to recreate resources
5. RDS will restore from latest automated backup

**Database Corruption**:
1. Create snapshot of current state (for investigation)
2. Restore from recent automated backup
3. Test restored database
4. Update ECS service to use restored RDS endpoint

## References

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [ECS Fargate Pricing](https://aws.amazon.com/fargate/pricing/)
- [RDS Pricing Calculator](https://aws.amazon.com/rds/pricing/)
- [Application Deployment Guide](../ai-testing-resource/README.md#deployment-to-aws)
- [AI Agent Instructions](../.claude/CLAUDE.md)
