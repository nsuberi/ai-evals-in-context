# Plan: Deploy and Run Steel Thread Tests

Deploy the AI Testing Resource to AWS using Terraform and local credentials, then run steel thread tests until passing, using CloudWatch logs to debug failures.

## Phase 1: Prerequisites Check

```bash
# Verify AWS credentials
aws sts get-caller-identity

# Verify tools
terraform --version
docker --version
jq --version
python3 --version
```

Ensure `ANTHROPIC_API_KEY` is set in environment.

## Phase 2: Terraform Deployment

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/terraform

# Initialize and apply
terraform init
terraform plan -var="anthropic_api_key=$ANTHROPIC_API_KEY"
terraform apply -var="anthropic_api_key=$ANTHROPIC_API_KEY" -auto-approve
```

This provisions: VPC, RDS PostgreSQL, ECS Cluster, ALB, ECR, API Gateway.

## Phase 3: Build and Deploy Application

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource/scripts
chmod +x deploy.sh
./deploy.sh
```

The script will:
1. Login to ECR (`671388079324.dkr.ecr.us-east-1.amazonaws.com`)
2. Build Docker image with git SHA tag
3. Push to ECR repository `ai-testing-resource-prod`
4. Update ECS task definition
5. Force new deployment
6. Wait for service stability

## Phase 4: Basic Verification

```bash
# Quick endpoint checks
curl -s https://portfolio.cookinupideas.com/ai-evals/health
curl -s -o /dev/null -w "%{http_code}" https://portfolio.cookinupideas.com/ai-evals/
```

Or use the verification script:
```bash
./scripts/verify-deployment.sh
```

## Phase 5: Run Steel Thread Tests

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

# Install test dependencies if needed
pip install pytest pytest-playwright
playwright install chromium

# Run all steel thread tests
pytest tests/playwright/test_steel_thread.py -v --portfolio-url=https://portfolio.cookinupideas.com
```

### Tests to Pass:

**TestPortfolioEntry** (3 tests):
- `test_portfolio_loads` - Portfolio homepage loads
- `test_accepting_ai_card_visible` - "Accepting AI" card visible
- `test_click_try_live_demo_navigates_to_app` - Demo link navigates to `/ai-evals`

**TestFullJourney** (4 tests):
- `test_full_journey_portfolio_to_viewer_tests` - Full path to `/viewer/tests`
- `test_health_endpoint_from_portfolio_journey` - Health check returns "healthy"
- `test_governance_dashboard_accessible` - `/governance/dashboard` accessible
- `test_ask_page_form_elements` - Form elements on `/ask` page

**TestDeployedAppErrors** (3 tests):
- `test_deployed_ask_endpoint_no_500` - POST to `/ask` doesn't return 500
- `test_deployed_ask_returns_structured_response` - Response is valid JSON
- `test_deployed_health_endpoint` - Health endpoint healthy

## Phase 6: Debug with CloudWatch Logs

When tests fail, check AWS logs:

```bash
# Tail logs in real-time
aws logs tail /ecs/ai-testing-resource-prod --follow --region us-east-1

# Filter for errors
aws logs filter-log-events \
    --log-group-name /ecs/ai-testing-resource-prod \
    --filter-pattern "ERROR" \
    --region us-east-1 \
    --output text

# Check ECS service events
aws ecs describe-services \
    --cluster ai-testing-resource-prod \
    --services ai-testing-resource-prod \
    --region us-east-1 \
    --query 'services[0].events[0:10]'
```

## Phase 7: Iterative Debug Loop

```
1. Run tests -> Identify failing test
2. Check CloudWatch logs for errors
3. Fix issue in code
4. Rebuild and push: docker build + docker push
5. Force redeploy: aws ecs update-service --force-new-deployment
6. Wait for stability
7. Re-run tests
8. Repeat until all 10 tests pass
```

### Quick Redeploy:
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
./scripts/deploy.sh
pytest tests/playwright/test_steel_thread.py -v --portfolio-url=https://portfolio.cookinupideas.com
```

## Critical Files

| Purpose | Path |
|---------|------|
| Terraform Main | `/terraform/main.tf` |
| Deploy Script | `/ai-testing-resource/scripts/deploy.sh` |
| Verify Script | `/ai-testing-resource/scripts/verify-deployment.sh` |
| Steel Thread Tests | `/ai-testing-resource/tests/playwright/test_steel_thread.py` |
| Dockerfile | `/ai-testing-resource/Dockerfile` |
| ECS Module | `/terraform/modules/ecs/main.tf` |

## Verification

Tests pass when:
```
pytest tests/playwright/test_steel_thread.py -v --portfolio-url=https://portfolio.cookinupideas.com
# Output: 10 passed
```
