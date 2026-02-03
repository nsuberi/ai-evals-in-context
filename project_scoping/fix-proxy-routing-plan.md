# Deployment Fix Plan: AI Testing Resource

## Problem Summary

The site at `https://portfolio.cookinupideas.com/ai-evals/` returns 500 error due to:
1. **Route collision**: Governance blueprint's `/` route registered at `/ai-evals/` instead of `/ai-evals/governance/`
2. **Missing template**: `governance/dashboard.html` not found (wrong search path)
3. **No deployment scripts**: Need local scripts for deploying to AWS

## Root Cause (from CloudWatch logs)

```
jinja2.exceptions.TemplateNotFound: governance/dashboard.html
```

The governance blueprint has its own `url_prefix='/governance'` but when registered with `url_prefix='/ai-evals'`, it **overrides** instead of **appending**, causing `/ai-evals/` to hit the governance dashboard.

---

## Implementation Steps

### Step 1: Fix Blueprint Registration with Proper URL Prefix Handling

**File**: `ai-testing-resource/app/__init__.py`

The key insight: Each blueprint has its own internal prefix that should be **combined** with APPLICATION_ROOT, not overridden.

```python
# Current (broken):
url_prefix = os.getenv('APPLICATION_ROOT', '') or None
app.register_blueprint(governance, url_prefix=url_prefix)  # Overrides '/governance'

# Fixed: Combine APPLICATION_ROOT with each blueprint's internal prefix
def combine_prefix(base, suffix):
    """Combine APPLICATION_ROOT with blueprint's own prefix"""
    if base and suffix:
        return f"{base}{suffix}"
    return base or suffix or None

url_prefix = os.getenv('APPLICATION_ROOT', '') or None

# tsr_api has internal prefix '/api/tsr'
app.register_blueprint(tsr_api, url_prefix=combine_prefix(url_prefix, '/api/tsr'))

# governance has internal prefix '/governance'
app.register_blueprint(governance, url_prefix=combine_prefix(url_prefix, '/governance'))

# app_bp has no internal prefix (root routes)
app.register_blueprint(app_bp, url_prefix=url_prefix)

# viewer_bp has internal prefix '/viewer'
app.register_blueprint(viewer_bp, url_prefix=combine_prefix(url_prefix, '/viewer'))
```

This makes routes work:
- **Locally (no proxy)**: `/`, `/governance/dashboard`, `/viewer/tests`
- **With proxy (APPLICATION_ROOT=/ai-evals)**: `/ai-evals/`, `/ai-evals/governance/dashboard`, `/ai-evals/viewer/tests`

### Step 2: Fix Template Search Path

**File**: `ai-testing-resource/app/__init__.py`

Add Jinja2 ChoiceLoader to search multiple template directories:

```python
from jinja2 import FileSystemLoader, ChoiceLoader

def create_app(testing=False):
    project_root = Path(__file__).parent.parent
    template_folder = project_root / 'templates'
    viewer_template_folder = project_root / 'viewer' / 'templates'

    app = Flask(__name__,
                template_folder=str(template_folder),
                static_folder=str(static_folder))

    # Add viewer templates as additional search path
    app.jinja_loader = ChoiceLoader([
        FileSystemLoader(str(template_folder)),
        FileSystemLoader(str(viewer_template_folder))
    ])
```

### Step 3: Update Blueprint Definitions (remove hardcoded prefixes)

Since we're now combining prefixes at registration time, remove the hardcoded prefixes from blueprint definitions:

**File**: `ai-testing-resource/viewer/governance.py`
```python
# Change from:
governance = Blueprint('governance', __name__, url_prefix='/governance')
# To:
governance = Blueprint('governance', __name__)
```

**File**: `ai-testing-resource/tsr/api.py`
```python
# Change from:
tsr_api = Blueprint('tsr_api', __name__, url_prefix='/api/tsr')
# To:
tsr_api = Blueprint('tsr_api', __name__)
```

**File**: `ai-testing-resource/viewer/routes.py`
```python
# Change from:
viewer_bp = Blueprint('viewer', __name__, url_prefix='/viewer')
# To:
viewer_bp = Blueprint('viewer', __name__)
```

### Step 4: Create Local Deployment Scripts

**File**: `ai-testing-resource/scripts/deploy.sh`

```bash
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
```

**File**: `ai-testing-resource/scripts/verify-deployment.sh`

```bash
#!/bin/bash
set -e

PORTFOLIO_URL="${PORTFOLIO_URL:-https://portfolio.cookinupideas.com}"
APP_URL="${APP_URL:-https://portfolio.cookinupideas.com/ai-evals}"

echo "=== Verifying Deployment ==="

# Check health endpoint
echo "Checking health endpoint..."
HEALTH=$(curl -s "$APP_URL/health")
if echo "$HEALTH" | grep -q "healthy"; then
    echo "Health check: PASS"
else
    echo "Health check: FAIL"
    echo "Response: $HEALTH"
    exit 1
fi

# Check root page (should not return 500)
echo "Checking root page..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/")
if [ "$STATUS" == "200" ]; then
    echo "Root page: PASS (HTTP $STATUS)"
else
    echo "Root page: FAIL (HTTP $STATUS)"
    exit 1
fi

# Check ask page
echo "Checking /ask page..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/ask")
if [ "$STATUS" == "200" ]; then
    echo "Ask page: PASS (HTTP $STATUS)"
else
    echo "Ask page: FAIL (HTTP $STATUS)"
    exit 1
fi

# Check governance dashboard
echo "Checking /governance/dashboard..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$APP_URL/governance/dashboard")
if [ "$STATUS" == "200" ]; then
    echo "Governance dashboard: PASS (HTTP $STATUS)"
else
    echo "Governance dashboard: FAIL (HTTP $STATUS)"
    exit 1
fi

echo ""
echo "=== All checks passed! ==="
```

---

## Files to Modify/Create

| File | Action | Purpose |
|------|--------|---------|
| `ai-testing-resource/app/__init__.py` | Modify | Fix blueprint registration + template loader |
| `ai-testing-resource/viewer/governance.py` | Modify | Remove hardcoded url_prefix |
| `ai-testing-resource/tsr/api.py` | Modify | Remove hardcoded url_prefix |
| `ai-testing-resource/viewer/routes.py` | Modify | Remove hardcoded url_prefix |
| `ai-testing-resource/scripts/deploy.sh` | Create | Local deployment script |
| `ai-testing-resource/scripts/verify-deployment.sh` | Create | Deployment verification |

---

## Verification

### 1. Local Testing (before deployment)
```bash
cd ai-testing-resource
docker compose down -v && docker compose build && docker compose up -d

# Test without APPLICATION_ROOT (local dev mode)
curl http://localhost:5001/              # Should show ask form
curl http://localhost:5001/governance/dashboard  # Should show governance
curl http://localhost:5001/health        # Should return healthy
curl http://localhost:5001/viewer/tests  # Should show test navigator
```

### 2. Deploy to AWS
```bash
cd ai-testing-resource
chmod +x scripts/deploy.sh scripts/verify-deployment.sh
./scripts/deploy.sh
```

### 3. Verify Deployment
```bash
./scripts/verify-deployment.sh
```

### 4. Run Steel Thread Tests
```bash
cd ai-testing-resource
pytest tests/playwright/test_steel_thread.py -v \
  --portfolio-url=https://portfolio.cookinupideas.com
```

Expected results:
- `/ai-evals/` returns ask form (HTTP 200)
- `/ai-evals/health` returns healthy
- `/ai-evals/governance/dashboard` shows TSR dashboard (HTTP 200)
- `/ai-evals/ask` POST returns structured JSON response

---

## How URL Routing Works After Fix

| Environment | APPLICATION_ROOT | Route | Actual Path |
|------------|------------------|-------|-------------|
| Local | (empty) | app_bp `/` | `/` |
| Local | (empty) | governance `/dashboard` | `/governance/dashboard` |
| Local | (empty) | viewer `/tests` | `/viewer/tests` |
| Production | `/ai-evals` | app_bp `/` | `/ai-evals/` |
| Production | `/ai-evals` | governance `/dashboard` | `/ai-evals/governance/dashboard` |
| Production | `/ai-evals` | viewer `/tests` | `/ai-evals/viewer/tests` |
