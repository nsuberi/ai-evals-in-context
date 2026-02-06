# Terraform AWS Deployment Plan: AI Testing Resource

## Overview

Deploy the ai-testing-resource Flask application to AWS using ECS Fargate, accessible via `portfolio.cookinupideas.com/ai-evals/*`. Reuses the existing ACM certificate and CloudFront distribution from proto-portal-showcase-hub.

## Architecture

```
Internet → Route 53 → CloudFront → /ai-evals/* → API Gateway → ECS Fargate (Spot)
                               → /* → S3 (existing static site)                └→ RDS PostgreSQL
```

**Approach**: Add the Flask application as a new CloudFront origin with path-based routing. This reuses:
- Existing ACM certificate: `arn:aws:acm:us-east-1:671388079324:certificate/4240573d-1c6a-44ec-9eee-eedc5f4c9157`
- Existing CloudFront distribution
- Existing Route 53 records

## Directory Structure

```
ai-evals-in-context/
└── terraform/
    ├── main.tf              # Root module - composes all modules
    ├── variables.tf         # Input variables
    ├── outputs.tf           # Output values (includes API Gateway URL for CloudFront)
    ├── providers.tf         # AWS provider config
    ├── backend.tf           # S3 state backend (same bucket as proto-portal)
    └── modules/
        ├── networking/      # VPC, public subnets, security groups
        ├── database/        # RDS PostgreSQL
        ├── ecs/             # Cluster, task definition, service, ECR
        └── api_gateway/     # HTTP API, VPC Link to ECS

proto-portal-showcase-hub/
├── src/
│   └── components/
│       └── Portfolio.tsx    # MODIFY: Add card for AI Evals prototype
└── terraform/
    ├── main.tf              # MODIFY: Add API Gateway origin + /ai-evals/* cache behavior
    └── (existing files)     # No other changes needed
```

## Terraform State & Plans Storage

Both projects share the same S3 bucket for state/plans:

| Project | S3 Bucket | State Key |
|---------|-----------|-----------|
| proto-portal-showcase-hub | `portfolio-portal-terraform-state` | `environments/prod/terraform.tfstate` |
| ai-evals-in-context | `portfolio-portal-terraform-state` | `ai-evals/environments/prod/terraform.tfstate` |

DynamoDB lock table: `terraform-state-locks` (shared)

## AWS Resources (Cost-Optimized for Low-Traffic Demo)

| Resource | Configuration | Purpose |
|----------|--------------|---------|
| VPC | 10.0.0.0/16, 2 public subnets only | Simplified networking |
| ECS Fargate Spot | 0.25 vCPU, 512MB RAM, public IP | Flask application |
| RDS PostgreSQL | db.t4g.micro, 20GB, single-AZ | TSR database (persistent) |
| API Gateway HTTP | Pay-per-request | Route traffic to ECS (no ALB needed) |
| ~~ALB~~ | REMOVED | API Gateway is cheaper for low traffic |
| ~~ElastiCache Redis~~ | DEFERRED | Add later if WebSocket needed |
| ~~NAT Gateway~~ | REMOVED | ECS in public subnet with public IP |
| Secrets Manager | 2 secrets | Anthropic API key, DB password |
| ECR | 1 repository | Docker images |

**Cost Reductions Applied:**
- No NAT Gateway: ECS tasks get public IPs directly (~$35 saved)
- API Gateway instead of ALB: ~$0.01 vs ~$18/month for low traffic
- No ElastiCache: Skip Redis for now, add later if WebSocket needed (~$12 saved)
- Fargate Spot: Up to 70% compute savings (~$6 saved)

**Trade-offs:**
- No WebSocket/real-time features (can add ALB + Redis later)
- Fargate Spot may have brief interruptions
- API Gateway has 29 second timeout (sufficient for AI responses)

**Future Upgrade Path (if WebSocket needed):**
1. Add ALB module to terraform
2. Add ElastiCache Redis
3. Switch API Gateway → ALB origin in CloudFront
4. Enable Flask-SocketIO in app config

**Reused from proto-portal-showcase-hub** (modifications required):
| Resource | Modification |
|----------|-------------|
| Portfolio.tsx | Add card linking to `/ai-evals/` |
| CloudFront | Add new origin (API Gateway) + cache behavior for `/ai-evals/*` |
| ACM Certificate | None - reuse existing |
| Route 53 | None - reuse existing |

## Estimated Monthly Cost: ~$19

- ECS Fargate Spot: ~$3
- RDS PostgreSQL (db.t4g.micro): ~$15
- API Gateway HTTP: ~$0.01 (at <10K requests/month)
- ECR, Secrets Manager: ~$1
- Note: Route 53 and ACM already covered by proto-portal-showcase-hub

## Security Tradeoffs: Public Subnets & No NAT Gateway

**What we're doing:**
- ECS tasks run in public subnets with public IPs
- No NAT Gateway (saves ~$35/month)

**Security implications:**
- ECS tasks are directly internet-accessible (mitigated by security groups)
- Security group ONLY allows traffic from API Gateway (not open to internet)
- RDS remains in private subnet (no public access)

**Risk assessment:**
- LOW RISK for demo: Security groups enforce network isolation
- ECS task only accepts traffic from API Gateway VPC endpoint
- Outbound internet access works (for Anthropic API calls) without NAT
- No sensitive data beyond API keys (stored in Secrets Manager)

**If you need higher security later:**
- Add private subnets + NAT Gateway (~$35/month)
- Move ECS to private subnets
- No application changes required

## Key Files to Create

### 1. `terraform/providers.tf`
- AWS provider with us-east-1 region
- Default tags for all resources

### 2. `terraform/variables.tf`
- `domain_name`: Subdomain for the application
- `route53_zone_id`: Z0990573XMA6PHFKL82S (existing)
- `anthropic_api_key`: Sensitive, passed via CI/CD
- Container sizing variables (CPU, memory)

### 3. `terraform/modules/networking/main.tf`
- VPC with DNS support
- 2 public subnets (for ECS) + 2 private subnets (for RDS)
- No NAT Gateway (ECS gets public IPs)
- Security groups: API Gateway → ECS (5000), ECS → RDS (5432)

### 4. `terraform/modules/database/main.tf`
- RDS PostgreSQL 15 (db.t4g.micro, single-AZ)
- DB subnet group in private subnets
- Auto-generated password in Secrets Manager

### 5. `terraform/modules/ecs/main.tf`
- ECR repository with lifecycle policy
- ECS cluster (Fargate Spot capacity provider)
- Task definition with environment variables and secrets
- Service in public subnet with public IP assignment
- Cloud Map service discovery for API Gateway VPC Link

### 6. `terraform/modules/api_gateway/main.tf`
- HTTP API (API Gateway v2)
- VPC Link to ECS service via Cloud Map
- Route: `ANY /{proxy+}` → ECS
- CORS configuration for CloudFront origin

### 7. `../proto-portal-showcase-hub/src/components/Portfolio.tsx` (MODIFY EXISTING)
Add a new card to the `implementedPrototypes` array:
```typescript
{
  title: "AI Testing Resource",
  description: "Interactive platform demonstrating AI evaluation practices. Features a three-version progression of an AI chatbot (verbose → hallucinating → accurate) with comprehensive testing pyramid, TSR governance, and real-time monitoring.",
  link: "/ai-evals/",
  tags: ["AI Evals", "Testing", "LLM", "Governance"],
  status: "Live Demo Available",
}
```

### 8. `../proto-portal-showcase-hub/terraform/main.tf` (MODIFY EXISTING)
- Add new CloudFront origin for API Gateway HTTP API
- Add cache behavior for `/ai-evals/*` path pattern (before default `/*`)
- Configure origin request policy to forward headers/cookies
- Disable caching for dynamic API content

### 9. `.github/workflows/deploy-terraform.yml` (DEFERRED)
- CI/CD integration deferred until local iteration validated
- Will add after successful local deployment

## Integration Points

### Existing Infrastructure (proto-portal-showcase-hub)
- **Reused**: ACM certificate `arn:aws:acm:us-east-1:671388079324:certificate/4240573d-1c6a-44ec-9eee-eedc5f4c9157`
- **Reused**: Route 53 hosted zone Z0990573XMA6PHFKL82S
- **Modified**: CloudFront distribution - add API Gateway origin + `/ai-evals/*` cache behavior
- **Modified**: Portfolio.tsx - add card linking to `/ai-evals/`
- **Separate**: New VPC for ECS + RDS (public + private subnets)

### Changes to proto-portal-showcase-hub/terraform/main.tf
```hcl
# Add API Gateway origin to CloudFront distribution
origin {
  domain_name = "xxxxxxxxxx.execute-api.us-east-1.amazonaws.com"  # From ai-evals terraform output
  origin_id   = "ai-evals-api"
  custom_origin_config {
    http_port              = 80
    https_port             = 443
    origin_protocol_policy = "https-only"
    origin_ssl_protocols   = ["TLSv1.2"]
  }
}

# Add cache behavior for /ai-evals/*
ordered_cache_behavior {
  path_pattern     = "/ai-evals/*"
  target_origin_id = "ai-evals-api"
  # ... caching disabled for dynamic API
}
```

### GitHub Actions OIDC
- Uses existing role: `arn:aws:iam::671388079324:role/github-actions-terraform-bootstrap`
- May need additional IAM permissions for ECS, ECR, Secrets Manager

## Environment Variables Mapping

| Application Config | AWS Source |
|-------------------|------------|
| ANTHROPIC_API_KEY | Secrets Manager |
| TSR_DATABASE_URL | Constructed from RDS endpoint + Secrets Manager password |
| ~~SOCKETIO_MESSAGE_QUEUE~~ | DEFERRED (no Redis yet) |
| SECRET_KEY | Secrets Manager (reuse DB password) |
| FLASK_DEBUG | Hardcoded "False" |
| ANTHROPIC_MODEL | Hardcoded "claude-sonnet-4-20250514" |

## Implementation Steps (Local Iteration)

All steps run locally with AWS credentials. CI/CD integration deferred to later phase.

### Phase 1: Create ai-evals-in-context Terraform
1. Create `terraform/` directory structure in ai-evals-in-context
2. Create `backend.tf` pointing to shared S3 bucket:
   ```hcl
   terraform {
     backend "s3" {
       bucket         = "portfolio-portal-terraform-state"
       key            = "ai-evals/environments/prod/terraform.tfstate"
       region         = "us-east-1"
       dynamodb_table = "terraform-state-locks"
       encrypt        = true
     }
   }
   ```
3. Create modules: networking, database, ecs, api_gateway
4. Create root main.tf composing modules

### Phase 2: Plan & Apply ai-evals Infrastructure
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/terraform
terraform init
terraform plan -out=tfplan-ai-evals-001.plan
# Review plan output
terraform apply tfplan-ai-evals-001.plan
```

### Phase 3: Build & Push Docker Image
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
# Get ECR repo URL from terraform output
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker build -t ai-testing-resource .
docker tag ai-testing-resource:latest <ecr-repo>:latest
docker push <ecr-repo>:latest
```

### Phase 4: Update proto-portal-showcase-hub
```bash
cd /Users/nathansuberi/Documents/GitHub/proto-portal-showcase-hub

# 1. Add portfolio card for AI Evals
# Edit src/components/Portfolio.tsx - add to implementedPrototypes array

# 2. Update CloudFront to route /ai-evals/* to API Gateway
# Edit terraform/main.tf - add API Gateway origin + cache behavior

# 3. Apply terraform changes
cd terraform
terraform plan -out=tfplan-proto-portal-002.plan
# Review plan output
terraform apply tfplan-proto-portal-002.plan

# 4. Rebuild and deploy portfolio site
cd ..
npm run build
# Deploy to S3 (aws s3 sync or terraform)
```

### Phase 5: Verify End-to-End
```bash
# Test direct API Gateway access
curl https://<api-gateway-url>/health

# Test via CloudFront
curl https://portfolio.cookinupideas.com/ai-evals/health
```

### Phase 6: CI/CD Integration (Future)
- Deferred until local iteration is validated
- Will add GitHub Actions workflows to both repos

## Local Testing & Log Viewing Loop

Use this loop when iterating on terraform and deployments locally:

### 1. Apply Terraform Changes
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/terraform
terraform plan -out=tfplan-ai-evals-XXX.plan
terraform apply tfplan-ai-evals-XXX.plan
```

### 2. Build & Push Docker Image
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 671388079324.dkr.ecr.us-east-1.amazonaws.com
docker build -t ai-testing-resource .
docker tag ai-testing-resource:latest 671388079324.dkr.ecr.us-east-1.amazonaws.com/ai-testing-resource-prod:latest
docker push 671388079324.dkr.ecr.us-east-1.amazonaws.com/ai-testing-resource-prod:latest
```

### 3. Force ECS Deployment (pick up new image)
```bash
aws ecs update-service --cluster ai-testing-resource-prod --service ai-testing-resource-prod --force-new-deployment
```

### 4. Watch Deployment Progress
```bash
# Watch ECS service events
aws ecs describe-services --cluster ai-testing-resource-prod --services ai-testing-resource-prod --query 'services[0].events[:5]'

# Wait for service to stabilize
aws ecs wait services-stable --cluster ai-testing-resource-prod --services ai-testing-resource-prod
```

### 5. View Application Logs
```bash
# Stream logs in real-time (Ctrl+C to stop)
aws logs tail /ecs/ai-testing-resource-prod --follow

# View recent logs
aws logs tail /ecs/ai-testing-resource-prod --since 30m

# Filter for errors
aws logs filter-log-events --log-group-name /ecs/ai-testing-resource-prod --filter-pattern "ERROR"

# View specific task logs (get task ID from ECS console or describe-tasks)
aws logs get-log-events --log-group-name /ecs/ai-testing-resource-prod --log-stream-name "ecs/ai-testing-resource/<task-id>"
```

### 6. Check API Gateway Logs (if enabled)
```bash
# API Gateway access logs (if configured)
aws logs tail /aws/apigateway/ai-evals-api --follow
```

### 7. Debug Common Issues
```bash
# Check if ECS task is running
aws ecs list-tasks --cluster ai-testing-resource-prod --service-name ai-testing-resource-prod

# Describe task to see status/errors
aws ecs describe-tasks --cluster ai-testing-resource-prod --tasks <task-arn>

# Check security group rules
aws ec2 describe-security-groups --group-ids <sg-id>

# Test RDS connectivity from local (requires VPN/bastion or public access)
psql -h <rds-endpoint> -U tsr_user -d tsr_db
```

### 8. Quick Health Check
```bash
# Direct to API Gateway
curl -v https://<api-gateway-id>.execute-api.us-east-1.amazonaws.com/health

# Via CloudFront (after integration)
curl -v https://portfolio.cookinupideas.com/ai-evals/health
```

## Terraform Plan Tracking

Keep numbered tfplan files to track iterations:

| Plan File | Repository | Description |
|-----------|------------|-------------|
| `tfplan-ai-evals-001.plan` | ai-evals-in-context | Initial infrastructure |
| `tfplan-ai-evals-002.plan` | ai-evals-in-context | (future iterations) |
| `tfplan-proto-portal-001.plan` | proto-portal-showcase-hub | (existing baseline if needed) |
| `tfplan-proto-portal-002.plan` | proto-portal-showcase-hub | Add API Gateway origin to CloudFront |

Plans stored locally in each repo's `terraform/` directory. Add to .gitignore:
```
*.plan
```

## Verification

1. **Infrastructure (ai-evals-in-context)**:
   ```bash
   cd ai-evals-in-context/terraform
   terraform plan  # Review before apply
   terraform apply
   # Note the API Gateway URL output
   ```

2. **Update CloudFront (proto-portal-showcase-hub)**:
   ```bash
   cd proto-portal-showcase-hub/terraform
   # Update main.tf with API Gateway origin
   terraform plan
   terraform apply
   ```

3. **Health check**:
   ```bash
   # Direct API Gateway (before CloudFront integration)
   curl https://<api-gateway-url>/health

   # Via CloudFront (after integration)
   curl https://portfolio.cookinupideas.com/ai-evals/health
   curl https://portfolio.cookinupideas.com/ai-evals/api/tsr/stats
   ```

4. **Portfolio card**:
   - Visit https://portfolio.cookinupideas.com
   - Verify "AI Testing Resource" card appears in implemented prototypes
   - Click card → should navigate to `/ai-evals/`

5. **Logs**:
   ```bash
   aws logs tail /ecs/ai-testing-resource-prod --follow
   ```

## Notes

- **Persistent database**: RDS PostgreSQL retains TSR data across deployments
- **Ephemeral embeddings**: ChromaDB rebuilt on container restart (acceptable for demo)
- **Public subnets for ECS**: Saves ~$35/month on NAT Gateway (see Security Tradeoffs section)
- **Fargate Spot**: May experience brief interruptions during capacity reclaim
- **Single task**: No redundancy, but sufficient for demo purposes
- **Path prefix**: Flask app must handle `/ai-evals` path prefix (via `APPLICATION_ROOT` or route prefix)
- **No caching**: CloudFront caching disabled for dynamic API routes
- **API Gateway timeout**: 29 seconds max - sufficient for most AI responses
- **WebSocket deferred**: Real-time monitoring disabled until ALB + Redis added
