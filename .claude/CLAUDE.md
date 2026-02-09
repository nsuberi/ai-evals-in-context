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

## Development Workflow

This project uses a breadboarding/affordances-first approach. The persistent affordances reference at `.claude/affordances.md` tracks all places, UI/code/data affordances, wiring, and component templates with sequential IDs (U for UI, N for code, D for data).

### Before Modifications

1. Read `.claude/affordances.md` to identify affected affordances
2. Check the Wiring table for downstream dependencies of anything you plan to change
3. Note new affordances that will be needed

### Key Patterns

- Use `python3` not `python` on this machine
- Phase config lives in `viewer/narrative.py` PHASES dict; navigation renders from `short_title`
- Templates at `templates/narrative/`, components at `templates/components/`
- CSS follows BEM naming convention with `--modifier` variants in `static/css/design-system.css`
- Collapsible macro: `{% from "components/collapsible.html" import collapsible %}`
- Tests use pytest with `client` fixture from `conftest.py`
- Existing E2E test failures in `test_ask_flow.py` are pre-existing (missing ANTHROPIC_API_KEY)

### Secrets & Environment

- The `ANTHROPIC_API_KEY` is stored in a local `.env` file at the project root (`ai-testing-resource/.env`). This file is gitignored and must never be committed.
- Copy `.env.example` to `.env` and fill in values for local development.
- In production, secrets are managed via AWS Secrets Manager (see Deployment section).

### After Completing Work

Update `.claude/affordances.md`:
1. Add new places, affordances, and wiring entries to the appropriate tables
2. Continue ID sequences (check highest existing ID in each prefix)
3. Update the "Last updated" date

### Linting

**Always run linting before committing any code.** The project uses three linting tools (installed in `.venv`):

1. **black** (formatter) — auto-formats Python code for consistent style.
2. **flake8** (linter) — catches unused imports, undefined names, and style issues.
3. **mypy** (type checker) — optional static type checking.

**Commands** (run from `ai-testing-resource/`):

```bash
# Activate the virtualenv first
source .venv/bin/activate

# Auto-format all changed files with black
black <file_or_directory>

# Check formatting without changing files
black --check <file_or_directory>

# Lint with flake8 (exclude venv, allow 120-char lines)
flake8 --exclude .venv,__pycache__ --max-line-length 120 <file_or_directory>

# Type check (optional, for files with annotations)
mypy <file_or_directory>
```

**Workflow**: Run `black` first to fix formatting, then `flake8` to catch remaining issues. Fix any flake8 errors (especially F-codes like unused imports) before committing.

### Git Commits

When work is complete and the user asks to commit:
- **Run linting first** — `black` then `flake8` on all changed files before staging.
- **Run tests before committing.** The `ANTHROPIC_API_KEY` is available locally via `.env`, so all test suites will run (API-dependent tests auto-skip only when the key is absent, e.g. in CI without secrets).
  ```bash
  source .venv/bin/activate
  # Load the API key from .env
  export $(grep -v '^#' .env | xargs)

  # Unit tests (fast, no API calls)
  python3 -m pytest tests/unit/ -v

  # E2E tests
  python3 -m pytest tests/e2e/ -v

  # Integration tests (chroma + AI service + RAG pipeline — makes API calls)
  python3 -m pytest tests/integration/ -v

  # Security and acceptance tests (make API calls)
  python3 -m pytest tests/security/ tests/acceptance/ -v
  ```
  For routine commits, run **unit + e2e** at minimum. Run the full suite (including integration, acceptance, security, performance, ai_acceptance) when changes touch AI service logic, prompts, RAG pipeline, or response handling:
  ```bash
  # Full suite (excludes playwright/steelthread which need a running server + browser)
  python3 -m pytest tests/unit/ tests/e2e/ tests/integration/ tests/acceptance/ tests/security/ tests/performance/ tests/ai_acceptance/ -v
  ```
  **Playwright / Steel Thread tests (major changes only):**
  The `tests/playwright/` and `tests/steelthread/` suites run a real browser against a running server. Use these for major changes (new routes, template overhauls, navigation changes, CSS/layout rework). They use Docker Compose to spin up the full stack:
  ```bash
  # 1. Install playwright and its browser binaries (one-time setup)
  pip install playwright
  playwright install chromium

  # 2. Start the app stack in the background (postgres + redis + flask)
  #    The api service builds from Dockerfile and serves on localhost:5001
  docker compose up -d --build

  # 3. Wait for the api container to be healthy
  docker compose ps  # confirm "tsr-api" shows "healthy"

  # 4. Run playwright browser tests against the local server
  python3 -m pytest tests/playwright/test_browser.py --base-url http://localhost:5001 -v

  # 5. Run steel thread tests against the local server
  python3 -m pytest tests/steelthread/ --base-url http://localhost:5001 -v

  # 6. To also run the playwright steel thread (hits deployed portfolio site)
  python3 -m pytest tests/playwright/test_steel_thread.py -v

  # 7. Tear down when done
  docker compose down
  ```
  Notes:
  - `docker-compose.yml` maps container port 5000 to host port **5001** — use `--base-url http://localhost:5001`.
  - The `ANTHROPIC_API_KEY` env var is passed through from your shell to the container. Make sure it's exported (`export $(grep -v '^#' .env | xargs)`) before `docker compose up`.
  - `docker-compose.ci.yml` is an override for CI (tmpfs postgres, no volumes). For local use, just use the base `docker-compose.yml`.
  - `test_steel_thread.py` in `tests/playwright/` hits the **deployed production** portfolio URL by default. Only run this to validate the live deployment, not local changes.

- Write clear, informative commit messages that explain *why* the change was made, not just *what* changed.
- Use conventional-style prefixes: `feat:`, `fix:`, `refactor:`, `docs:`, `test:`, `chore:` as appropriate.
- Keep the first line under 72 characters; add detail in the body if needed.
- Stage specific files rather than using `git add -A` to avoid committing secrets or unrelated changes.
- **Document architectural changes in the commit body.** When a commit introduces structural changes (new modules, changed data flow, refactored component boundaries, new routes/endpoints, template hierarchy changes), include an `Architecture:` section in the commit body. This is used to inform PR descriptions and generate architecture diagrams. Example:
  ```
  feat: add real-time trace monitoring via WebSocket

  Replace polling-based trace updates with WebSocket push.
  Reduces dashboard latency from ~5s to <200ms.

  Architecture:
  - New module: viewer/realtime.py (SocketIO event handlers)
  - Data flow: trace_inspector.py -> SocketIO -> browser JS listener
  - New dependency: flask-socketio added to requirements.txt
  - Template change: monitoring/traces.html now includes ws_client.js
  - Removed: polling timer in static/js/trace_refresh.js

  Co-Authored-By: Claude Opus 4.6 <noreply@anthropic.com>
  ```
  These notes don't need to be exhaustive — focus on what another developer (or a PR summary) would need to understand the structural impact of the change.

### Continuous Improvement

When you discover something useful about this project (gotchas, patterns, architecture decisions, debugging tips), add it to this CLAUDE.md so future sessions benefit. Examples:
- A non-obvious dependency between components
- A workaround for a known issue
- A pattern that should be followed for consistency
- A command or configuration that was hard to figure out

Keep notes concise and placed in the most relevant section.

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

**IMPORTANT: A healthy endpoint does not mean the deployment succeeded.** The health check may return `"healthy"` from a *previous* deployment's still-running task while the new deployment is failing. Always confirm the new code is actually live:

**Verify the deployment itself succeeded:**
```bash
# Check the ECS service — look at "deployments" array and task timestamps
aws ecs describe-services \
  --cluster ai-testing-resource-prod \
  --services ai-testing-resource-prod \
  --query 'services[0].{desiredCount:desiredCount,runningCount:runningCount,deployments:deployments[*].{status:status,runningCount:runningCount,desiredCount:desiredCount,createdAt:createdAt,updatedAt:updatedAt,taskDefinition:taskDefinition}}' \
  --output table

# Verify there is only ONE deployment with status "PRIMARY" and runningCount == desiredCount.
# If you see a second deployment with status "ACTIVE", the new deployment is still rolling out
# or failing. If runningCount is 0 on the PRIMARY deployment, tasks are crashing.

# Check when the running task was started (should be recent, after your deploy)
aws ecs list-tasks --cluster ai-testing-resource-prod --service-name ai-testing-resource-prod --query 'taskArns' --output text | \
  xargs -I {} aws ecs describe-tasks --cluster ai-testing-resource-prod --tasks {} \
  --query 'tasks[0].{startedAt:startedAt,lastStatus:lastStatus,taskDefinitionArn:taskDefinitionArn}' --output table
```

**If the deployment failed — check the logs:**
```bash
# Tail recent CloudWatch logs for startup errors or crash loops
aws logs tail /ecs/ai-testing-resource-prod --since 30m --follow

# If you need older logs or want to search for specific errors
aws logs filter-log-events \
  --log-group-name /ecs/ai-testing-resource-prod \
  --start-time $(date -v-1H +%s000) \
  --filter-pattern "ERROR"

# Check stopped tasks for the stop reason (e.g. OOM, health check failure, crash)
aws ecs list-tasks --cluster ai-testing-resource-prod --service-name ai-testing-resource-prod --desired-status STOPPED --query 'taskArns' --output text | \
  xargs -I {} aws ecs describe-tasks --cluster ai-testing-resource-prod --tasks {} \
  --query 'tasks[0].{stopCode:stopCode,stoppedReason:stoppedReason,stoppedAt:stoppedAt,containers:containers[0].{exitCode:exitCode,reason:reason}}' --output table
```

**Manual verification:**
- Visit `https://portfolio.cookinupideas.com/ai-evals/`
- Confirm the page content reflects your changes (not a stale cached version)

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

