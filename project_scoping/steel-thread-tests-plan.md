# Plan: Deploy Terraform and Write Steel Thread Tests

## Summary
Deploy the terraform infrastructure, update the portfolio card with playful messaging about "Accepting AI", and create Playwright steel thread tests.

---

## Part 1: Update Portfolio Card

### File to Modify
`/Users/nathansuberi/Documents/GitHub/proto-portal-showcase-hub/src/components/Portfolio.tsx`

### Current Card (lines 8-16)
```typescript
{
  title: "AI Testing Resource",
  description:
    "Interactive platform demonstrating AI evaluation practices. Features a three-version progression of an AI chatbot (verbose to hallucinating to accurate) with comprehensive testing pyramid, TSR governance, and real-time monitoring.",
  link: "/ai-evals/",
  tags: ["AI Evals", "Testing", "LLM", "Governance"],
  status: "Live Demo Available",
},
```

### Updated Card
```typescript
{
  title: "Accepting AI: A Testing Adventure",
  description:
    "Ready to embrace AI in your software? This interactive resource shows you how to test AI systems alongside all your classic SDLC favorites - unit tests, integration tests, E2E tests - with exciting new additions like behavioral evals and hallucination detection! Watch a chatbot evolve from overly verbose to accidentally creative (oops, hallucinations!) to reliably accurate. Your testing pyramid just got a shiny new top!",
  link: "/ai-evals/",
  tags: ["Accepting AI", "Testing Pyramid", "Evals", "SDLC", "Governance"],
  status: "Live Demo Available",
},
```

---

## Part 2: Terraform Deployment (Run Locally)

### Step 1: Build and Push Docker Image to ECR

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 671388079324.dkr.ecr.us-east-1.amazonaws.com

# Build the image
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
docker build -t ai-testing-resource-prod:latest .

# Tag and push to ECR
docker tag ai-testing-resource-prod:latest 671388079324.dkr.ecr.us-east-1.amazonaws.com/ai-testing-resource-prod:latest
docker push 671388079324.dkr.ecr.us-east-1.amazonaws.com/ai-testing-resource-prod:latest
```

### Step 2: Initialize and Apply Terraform

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/terraform

# Initialize terraform
terraform init

# Plan and review changes
terraform plan -out=tfplan.plan

# Apply the plan
terraform apply tfplan.plan
```

### Step 3: Force ECS Service Update

```bash
aws ecs update-service \
  --cluster ai-testing-resource-prod \
  --service ai-testing-resource-prod \
  --force-new-deployment \
  --region us-east-1
```

### Step 4: Wait for ECS Service to Stabilize

```bash
aws ecs wait services-stable \
  --cluster ai-testing-resource-prod \
  --services ai-testing-resource-prod \
  --region us-east-1
```

### Step 5: Verify ALB Health Endpoint

```bash
curl -s https://ai-testing-resource-prod-977104126.us-east-1.elb.amazonaws.com/ai-evals/health
```

Expected output: `{"service":"ai-testing-resource","status":"healthy"}`

---

## Part 3: Deploy Portfolio Update

After updating Portfolio.tsx, deploy the portfolio:

```bash
cd /Users/nathansuberi/Documents/GitHub/proto-portal-showcase-hub

# Build and deploy
npm run build
# (Or whatever deployment command the portfolio uses)
```

---

## Part 4: Steel Thread Playwright Tests

### Files to Create

1. **ai-testing-resource/tests/playwright/conftest.py** (update)
2. **ai-testing-resource/tests/playwright/test_steel_thread.py** (create)

### conftest.py Changes

Add pytest CLI options and fixtures for `--portfolio-url` and `--base-url`:
- `portfolio_url` fixture defaults to `https://portfolio.cookinupideas.com`
- `base_url` fixture defaults to `http://localhost:5001` (for local) or env var
- `browser_context_args` fixture for HTTPS handling

### test_steel_thread.py - Test Cases

Tests follow the user journey from portfolio to app:

1. **test_portfolio_loads** - Portfolio homepage loads
2. **test_accepting_ai_card_visible** - Card with "Accepting AI" title is visible
3. **test_click_try_live_demo_navigates_to_app** - Click "Try Live Demo" → navigates to /ai-evals
4. **test_full_journey_portfolio_to_viewer_tests** - Full path: Portfolio → Card → App → /viewer/tests
5. **test_health_endpoint_from_portfolio_journey** - Journey + health check returns 200
6. **test_governance_dashboard_accessible** - Journey + navigate to /governance/dashboard
7. **test_ask_page_form_elements** - Journey + verify form elements on /ask page

---

## Part 5: Run Verification Tests (Run Locally)

### Install Playwright Dependencies

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
pip install playwright pytest-playwright
playwright install chromium
```

### Run Steel Thread Tests

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
pytest tests/playwright/test_steel_thread.py \
  --portfolio-url=https://portfolio.cookinupideas.com \
  -v
```

---

## Files Modified

| File | Action | Description |
|------|--------|-------------|
| `proto-portal-showcase-hub/src/components/Portfolio.tsx` | Update | New card title and playful description |
| `ai-testing-resource/tests/playwright/conftest.py` | Update | Add CLI options and fixtures |
| `ai-testing-resource/tests/playwright/test_steel_thread.py` | Create | Steel thread journey tests |

## Verification Checklist

- [ ] Portfolio card updated with "Accepting AI" messaging
- [ ] Docker image built and pushed to ECR
- [ ] Terraform applied successfully
- [ ] ECS service stable with 1/1 tasks
- [ ] Portfolio deployed with updated card
- [ ] ALB health endpoint returns 200 with "healthy"
- [ ] All steel thread tests pass (portfolio → card → app navigation)
