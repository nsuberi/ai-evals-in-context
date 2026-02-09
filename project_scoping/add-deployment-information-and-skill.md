# Deployment Documentation Plan

## Overview
Create comprehensive deployment guidance for two distinct build and deploy processes:
1. **Flask App (ai-evals-in-context)**: Docker → ECR → ECS Fargate
2. **Base Portfolio (proto-portal-showcase-hub)**: React/Next.js → S3 + CloudFront

These components integrate at the infrastructure level - the portfolio CloudFront routes `/ai-evals/*` traffic to the Flask app's ALB.

## Architecture Context

### Flask App Deployment
- **Location**: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource`
- **Stack**: Flask Python app in Docker container
- **Infrastructure**: ECS Fargate (0.25 vCPU, 512MB), RDS PostgreSQL, ALB, API Gateway
- **Build Process**: Docker build → ECR push → ECS task definition update
- **Deployment Scripts**: `scripts/deploy.sh`, `scripts/verify-deployment.sh`
- **URL**: `https://portfolio.cookinupideas.com/ai-evals/`
- **Proxy Awareness**: Uses `APPLICATION_ROOT=/ai-evals` environment variable

### Portfolio Deployment
- **Location**: `/Users/nathansuberi/Documents/GitHub/proto-portal-showcase-hub`
- **Stack**: React/Next.js static site
- **Infrastructure**: S3 bucket + CloudFront CDN + Route 53
- **Build Process**: Static site generation → S3 sync → CloudFront invalidation
- **URL**: `https://portfolio.cookinupideas.com`
- **Integration**: Routes `/ai-evals/*` to Flask app ALB via CloudFront origin

## Implementation Plan

### Phase 1: ai-evals-in-context Repository (Current Repo)

#### 1.1 Expand `.claude/CLAUDE.md`
**File**: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context/.claude/CLAUDE.md`

**Add sections**:
- Flask App Deployment Overview (architecture summary)
- Prerequisites (AWS credentials, Terraform, Docker)
- Infrastructure Deployment (Terraform workflow)
- Application Deployment (deploy.sh script workflow)
- Verification Steps (verify-deployment.sh)
- Environment Variables Reference (all vars with descriptions)
- Integration with Portfolio (CloudFront routing notes)
- Troubleshooting Common Issues (proxy routing, health checks, secrets)

**Keep existing content**: Proxy configuration, script usage, TF_VAR_ syntax, AWS credentials

#### 1.2 Add Deployment Section to `README.md`
**File**: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource/README.md`

**Insert after "Docker Commands Reference" section** (line 246):

New section with:
- Deployment to AWS heading
- Architecture diagram reference
- Prerequisites checklist
- Step-by-step deployment instructions:
  1. Deploy infrastructure with Terraform
  2. Build and push Docker image
  3. Update ECS service
  4. Verify deployment
- Links to terraform/README.md for infrastructure details
- Environment variable notes
- Cost estimate (~$19/month)
- Integration notes with portfolio

#### 1.3 Create `terraform/README.md`
**File**: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context/terraform/README.md` (NEW)

**Comprehensive infrastructure documentation**:
- Overview of architecture components
- State management (S3 backend, DynamoDB locks)
- Module structure:
  - `networking/` - VPC, subnets, security groups
  - `database/` - RDS PostgreSQL with Secrets Manager
  - `ecs/` - ECR, Fargate cluster, task definition, service
  - `alb/` - Application Load Balancer with HTTPS
  - `api_gateway/` - HTTP API with VPC Link
- Required variables with descriptions
- Optional variables with defaults
- Deployment workflow:
  1. Initialize Terraform
  2. Plan with variables
  3. Apply infrastructure
  4. Capture outputs
- Outputs reference (ALB DNS, ECR URL, API Gateway URL)
- Integration with portfolio (passing ALB domain)
- Cost breakdown by service

#### 1.4 Create Local Deployment Verification Skill
**File**: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context/.claude/skills/deploy-from-local.xml` (NEW)

**Comprehensive local deployment verification skill** (`/deploy-from-local`) that:

1. **Environment Verification**:
   - Check AWS credentials exist (`~/.aws/credentials`)
   - Verify AWS CLI is installed and configured
   - Check Docker is running
   - Verify Terraform is installed
   - Check Node.js/npm versions (for portfolio builds)
   - Validate required environment variables

2. **Flask App Build Verification**:
   - Navigate to `ai-testing-resource/`
   - Check `.env` file exists with `ANTHROPIC_API_KEY`
   - Test Docker build locally:
     ```bash
     docker build -t ai-testing-resource:local .
     ```
   - Verify build succeeds without errors
   - Check image size and layers
   - Test container startup locally:
     ```bash
     docker run -p 5000:5000 --env-file .env ai-testing-resource:local
     ```
   - Verify health endpoint responds

3. **Portfolio Build Verification** (if proto-portal-showcase-hub accessible):
   - Navigate to portfolio repo
   - Check for npm/package.json
   - Detect Node.js version requirements
   - Handle npm version issues:
     - Check for `.nvmrc` or `package.json` engines field
     - Suggest `nvm use` if Node version mismatch
     - Offer to install dependencies with correct npm version
   - Run portfolio build:
     ```bash
     npm install
     npm run build
     ```
   - Verify build artifacts created
   - Check for build warnings/errors

4. **Terraform Verification**:
   - Navigate to `terraform/`
   - Run `terraform init`
   - Run `terraform validate`
   - Run `terraform plan` (dry-run, no apply)
   - Report any configuration issues
   - Verify state backend is accessible

5. **Integration Testing**:
   - Test Flask app locally with Docker Compose
   - Verify all services start (postgres, redis, api)
   - Run pytest suite
   - Check for failing tests
   - Report test results

6. **Deployment Simulation**:
   - Show what WOULD happen during deployment
   - Preview ECR push (without actually pushing)
   - Preview ECS task definition changes
   - Estimate deployment time
   - Show verification endpoints to check

7. **Issue Detection & Resolution**:
   - Detect common issues:
     - Missing environment variables
     - AWS credential problems
     - Docker daemon not running
     - Node/npm version mismatches
     - Port conflicts
     - Terraform state lock issues
   - Provide automated fixes where possible
   - Link to troubleshooting documentation

8. **Deployment Options** (after verification passes):
   - **Dry run only** - Just verify, don't deploy
   - **Local Docker only** - Test locally with docker-compose
   - **Deploy Flask app** - Run `scripts/deploy.sh`
   - **Deploy portfolio** - Run portfolio deployment scripts
   - **Full deployment** - Deploy both components

**Skill structure**:
```xml
<skill name="deploy-from-local" version="1.0">
  <description>Verify local deployment setup and test builds before deploying</description>
  <trigger>deploy-from-local</trigger>
  <instructions>
    You are a deployment verification assistant. Your job is to:

    1. Verify the local environment is ready for deployment
    2. Test all builds locally to catch issues early
    3. Handle common problems like npm version mismatches
    4. Run comprehensive verification before any actual deployment
    5. Provide clear, actionable feedback on any issues

    WORKFLOW:

    Step 1: Environment Check
    - Verify AWS credentials, Docker, Terraform, Node.js
    - Report versions and any issues

    Step 2: Flask App Verification
    - Test Docker build locally
    - Start container and check health
    - Run pytest to verify tests pass

    Step 3: Portfolio Verification (if accessible)
    - Check Node.js version requirements
    - Handle npm version issues:
      * Check package.json engines field
      * Suggest nvm use if version mismatch
      * Install dependencies with correct version
    - Run build and verify success
    - Check for build warnings

    Step 4: Terraform Validation
    - Init, validate, and plan (dry-run)
    - Report configuration issues

    Step 5: Integration Testing
    - Start docker-compose services
    - Run full test suite
    - Verify all services healthy

    Step 6: Report & Recommendations
    - Summarize all checks
    - List any issues found
    - Provide fix instructions
    - Ask if user wants to proceed with deployment

    IMPORTANT:
    - Never deploy without verification passing
    - Handle npm/Node version issues gracefully
    - Provide specific error messages with solutions
    - Test builds locally before AWS deployment
    - Stop at first critical error and provide guidance
  </instructions>
</skill>
```

**This skill ensures "it all works" by**:
- Testing complete build process locally
- Catching npm/Node version issues early
- Verifying all dependencies are correct
- Running tests before deployment
- Simulating deployment without actually deploying
- Providing clear feedback on any issues

### Phase 2: proto-portal-showcase-hub Repository (Separate Step)

**Note**: These changes must be made in a separate session after switching to that repository.

#### 2.1 Update `CLAUDE.md`
**File**: `/Users/nathansuberi/Documents/GitHub/proto-portal-showcase-hub/CLAUDE.md`

**Add sections**:
- Portfolio Deployment Overview
- Monorepo architecture notes
- AI Evals integration configuration
- CloudFront routing setup (ai_evals_alb_domain variable)
- Build and deployment script workflow
- Integration testing considerations

#### 2.2 Add Integration Notes to `README.md`
**File**: `/Users/nathansuberi/Documents/GitHub/proto-portal-showcase-hub/README.md`

**Add to "Production Deployment" section**:
- Integrated Prototypes subsection
- AI Testing Resource integration details
- CloudFront path routing (`/ai-evals/*`)
- Terraform variable configuration
- Link to ai-evals-in-context repository

## Critical Files Reference

### ai-evals-in-context Repository
- `.claude/CLAUDE.md` - AI agent deployment instructions
- `ai-testing-resource/README.md` - User-facing deployment guide
- `terraform/README.md` - Infrastructure documentation (NEW)
- `.claude/skills/deploy-from-local.xml` - Local deployment verification skill (NEW)
- `terraform/main.tf` - Infrastructure composition (reference only)
- `terraform/variables.tf` - Configuration variables (reference only)
- `scripts/deploy.sh` - Application deployment script (reference only)
- `scripts/verify-deployment.sh` - Verification script (reference only)

### proto-portal-showcase-hub Repository (separate session)
- `CLAUDE.md` - Portfolio deployment notes
- `README.md` - Integration documentation
- `terraform/main.tf` - CloudFront configuration reference

## Key Information to Document

### Flask App Deployment Process
1. **Infrastructure Setup** (one-time):
   ```bash
   cd terraform/
   terraform init
   export TF_VAR_anthropic_api_key="$ANTHROPIC_API_KEY"
   terraform plan -out=tfplan.plan
   terraform apply tfplan.plan
   ```

2. **Application Deployment** (repeatable):
   ```bash
   cd ai-testing-resource/
   ./scripts/deploy.sh
   ```

3. **Verification**:
   ```bash
   ./scripts/verify-deployment.sh
   ```

### Portfolio Deployment Process
1. **Build**:
   ```bash
   ./scripts/build.sh
   ```

2. **Deploy Infrastructure**:
   ```bash
   ./scripts/deploy-infrastructure.sh
   ```

3. **Deploy Site**:
   ```bash
   ./scripts/deploy-site.sh
   ```

### Integration Configuration
- Portfolio CloudFront needs `ai_evals_alb_domain` variable
- Get ALB domain from Flask app Terraform output:
  ```bash
  cd ai-evals-in-context/terraform
  terraform output -raw alb_dns_name
  ```
- Pass to portfolio Terraform:
  ```bash
  cd proto-portal-showcase-hub/terraform
  terraform apply -var="ai_evals_alb_domain=<alb-domain>"
  ```

## Environment Variables Documentation

### Flask App Production Variables
- `ANTHROPIC_API_KEY` - Claude API key (Secrets Manager)
- `TSR_DATABASE_URL` - PostgreSQL connection string (Secrets Manager)
- `APPLICATION_ROOT` - Set to `/ai-evals` for proxy routing
- `SECRET_KEY` - Flask session secret
- `FLASK_HOST` - `0.0.0.0` for container
- `FLASK_PORT` - `5000` (default)
- `CHROMA_PATH` - `/app/chroma_db` (container path)
- `MONITORING_ENABLED` - `True` for production
- `TRACE_RETENTION_HOURS` - `24` (default)

### CI/CD Variables (GitHub Actions)
- `TSR_API_TOKEN` - For uploading TSRs in CI
- `TSR_API_URL` - Test Summary Report API endpoint
- AWS OIDC role: `arn:aws:iam::671388079324:role/github-actions-terraform-bootstrap`

## Verification Steps

After deployment, verify:
1. Health endpoint: `https://portfolio.cookinupideas.com/ai-evals/health`
2. Main app: `https://portfolio.cookinupideas.com/ai-evals/`
3. Ask page: `https://portfolio.cookinupideas.com/ai-evals/ask`
4. Dashboard: `https://portfolio.cookinupideas.com/ai-evals/governance/dashboard`
5. CloudWatch logs show no errors
6. ECS service shows healthy tasks
7. RDS database is accessible from ECS

## Cost Breakdown

### Flask App Infrastructure (~$19/month)
- ECS Fargate Spot (0.25 vCPU, 512MB): ~$3/month
- RDS PostgreSQL (db.t4g.micro, 20GB): ~$15/month
- ALB: ~$16/month (NOTE: This may be shared with portfolio)
- API Gateway: ~$0.01/month (low traffic)
- ECR storage: ~$0.50/month
- Secrets Manager: ~$0.40/month

### Portfolio Infrastructure (~$5/month)
- S3 storage + requests: ~$1/month
- CloudFront: ~$1/month (low traffic)
- Route 53: ~$0.50/month

**Note**: ALB cost may be shared if portfolio uses same ALB, reducing total cost.

## Implementation Order

1. ✅ Phase 1.1: Expand `.claude/CLAUDE.md` in ai-evals-in-context
2. ✅ Phase 1.2: Add deployment section to `ai-testing-resource/README.md`
3. ✅ Phase 1.3: Create `terraform/README.md`
4. ✅ Phase 1.4: Create local deployment verification skill `.claude/skills/deploy-from-local.xml`
5. ✅ Phase 1.5: **Test the skill** - Run `/deploy-from-local` to verify it works end-to-end
6. ⏭️  Phase 2: Update proto-portfolio-showcase-hub (separate session)

## Success Criteria

- [ ] CLAUDE.md provides clear AI agent instructions for deployment
- [ ] README.md has user-friendly deployment section with prerequisites
- [ ] terraform/README.md documents infrastructure in detail
- [ ] `/deploy-from-local` skill provides comprehensive verification
- [ ] Skill handles npm/Node version issues gracefully
- [ ] Skill tests builds locally before deployment
- [ ] Skill verifies "it all works" end-to-end
- [ ] All documentation references correct file paths
- [ ] Integration between portfolio and Flask app is clearly explained
- [ ] Cost estimates are included for transparency
- [ ] Verification steps are comprehensive
- [ ] Both local and CI/CD deployment paths are documented
