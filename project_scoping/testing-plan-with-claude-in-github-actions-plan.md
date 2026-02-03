# Verification Plan: Testing Infrastructure & CI/CD Pipeline

## Overview

Verify the complete testing infrastructure works both locally and in CI/CD, using GitHub Actions with Claude integration to iteratively fix issues until achieving a green pipeline. This prepares the codebase for future AWS/Terraform deployment (not implemented in this phase).

## Critical Issues Identified

### Issue 1: Workflow File Location (BLOCKING)
- **Current**: `ai-testing-resource/.github/workflows/ai-app-ci.yml`
- **Required**: `.github/workflows/ai-app-ci.yml` (repo root)
- **Impact**: Workflow will not trigger until moved to correct location
- **Fix**: Move file to repo root

### Issue 2: Missing Git in Docker Container
- **Current**: Dockerfile doesn't install git
- **Impact**: TSR generation may need git for additional metadata
- **Fix**: Add `git` to apt-get install in Dockerfile:7

### Issue 3: Redundant Test Execution
- **Current**: docker-compose.ci.yml runs tests, then workflow runs them again (line 41)
- **Impact**: Doubles test execution time
- **Fix**: Remove explicit pytest call in workflow, let CI compose handle it

---

## Phase 1: Local Verification

### 1.1 Environment Prerequisites

**Check local environment:**
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource

# Verify tools
docker --version
docker-compose --version
python3 --version

# Verify API key available
echo $ANTHROPIC_API_KEY  # Should output key
```

**Success Criteria:**
- Docker installed and running
- Python 3.9+ available
- ANTHROPIC_API_KEY set in environment

---

### 1.2 Run Tests Locally (Native Python)

**Setup virtual environment:**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env to add ANTHROPIC_API_KEY
```

**Run test categories incrementally:**
```bash
# Unit tests (no API key needed)
pytest tests/unit/ -v

# Security tests
pytest tests/security/ -v

# Integration tests (may need ChromaDB)
pytest tests/integration/ -v

# AI evaluations (will consume API tokens)
pytest tests/evals/ -v

# Run ALL tests with JUnit XML output
mkdir -p results
pytest tests/ --junitxml=results/test-results.xml -v
```

**Success Criteria:**
- Unit and security tests pass completely
- JUnit XML generated at `results/test-results.xml`
- AI evals execute (V1/V2 may fail intentionally, V3 should pass)

---

### 1.3 Run Tests with Docker Compose

**Start services and run tests:**
```bash
# Copy environment configuration
cp .env.docker .env
echo "ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY" >> .env

# Use CI configuration (auto-runs tests)
docker compose -f docker-compose.yml -f docker-compose.ci.yml up

# Or start services and run tests manually
docker compose up -d
docker compose exec api pytest tests/ --junitxml=results/test-results.xml -v

# Check logs
docker compose logs api | grep -E "PASSED|FAILED"

# Cleanup
docker compose down -v
```

**Success Criteria:**
- All services start and reach "healthy" status
- Tests execute inside container
- Results accessible at `results/test-results.xml`
- No container crashes or OOM errors

---

### 1.4 Generate TSR Locally

**Generate Test Summary Report:**
```bash
# Start Docker services
docker compose up -d

# Generate TSR
docker compose exec api python scripts/generate_tsr.py \
  --results-dir results/ \
  --codebase-sha $(git rev-parse HEAD) \
  --environment local \
  --triggered-by developer \
  --output tsr.json \
  --pretty

# Copy TSR to host and inspect
docker compose exec api cat tsr.json > tsr-local.json
cat tsr-local.json | python3 -m json.tool | less

# Check decision
cat tsr-local.json | python3 -c "
import sys, json
tsr = json.load(sys.stdin)
print(f'Decision: {tsr[\"go_no_go_decision\"]}')
print(f'Reason: {tsr[\"decision_reason\"]}')
"

# Cleanup
docker compose down -v
```

**Success Criteria:**
- TSR JSON file created successfully
- Contains go/no-go decision ("go", "no_go", or "pending_review")
- All test results aggregated correctly
- Version manifest populated with git SHA

---

## Phase 2: GitHub Actions Fixes

### 2.1 Fix Workflow File Location

**Move workflow to correct location:**
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context

# Ensure .github/workflows exists at repo root
mkdir -p .github/workflows

# Move workflow file
mv ai-testing-resource/.github/workflows/ai-app-ci.yml .github/workflows/ai-app-ci.yml

# Remove empty directory
rmdir ai-testing-resource/.github/workflows
rmdir ai-testing-resource/.github
```

**Verify workflow uses correct working-directory:**
- All steps should have `working-directory: ./ai-testing-resource`
- This is already correct in the workflow file

---

### 2.2 Add Git to Docker Container

**Update Dockerfile:**

File: `ai-testing-resource/Dockerfile`

Change line 6-7 from:
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*
```

To:
```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*
```

---

### 2.3 Fix Redundant Test Execution (Optional)

**Current Issue:**
- `docker-compose.ci.yml` runs tests via command (line 15-20)
- Workflow runs tests again with `docker compose exec` (line 41)

**Option A (Recommended): Let CI Compose Handle Tests**
Remove lines 40-41 from workflow and let docker-compose.ci.yml run tests automatically. Extract results after compose up completes.

**Option B: Remove Auto-Test from CI Compose**
Change docker-compose.ci.yml command to just start the Flask app, let workflow run tests explicitly.

**Decision:** Use Option A - let CI compose auto-run tests, workflow just extracts results.

---

### 2.4 Verify GitHub Secrets

**Check required secrets:**
```bash
# List secrets
gh secret list

# Set ANTHROPIC_API_KEY if missing
gh secret set ANTHROPIC_API_KEY
# Paste key when prompted
```

**Required secrets:**
- `ANTHROPIC_API_KEY` - Required for AI evaluations and Claude integration
- `TSR_API_URL` - Optional (defaults to localhost)
- `TSR_API_TOKEN` - Optional (for future TSR upload)

**Success Criteria:**
- ANTHROPIC_API_KEY secret exists
- Can view secret name in repo settings

---

## Phase 3: GitHub Actions Testing

### 3.1 Create Test Branch and PR

**Create test branch:**
```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context

# Create and checkout test branch
git checkout -b test/verify-ci-pipeline

# Make a small, safe change (document testing)
echo "\n<!-- Testing CI/CD pipeline verification -->" >> ai-testing-resource/README.md

# Commit changes
git add .
git commit -m "test: verify CI/CD pipeline

Testing infrastructure validation:
- GitHub Actions workflow execution
- Docker Compose in CI environment
- Test execution and TSR generation
- Claude integration (PR reviews and @mentions)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"

# Push to remote
git push -u origin test/verify-ci-pipeline
```

**Create pull request:**
```bash
gh pr create \
  --title "Test: Verify CI/CD Pipeline" \
  --body "## Purpose
Verify the complete testing infrastructure works in CI/CD:

**Local Verification:**
- [x] Tests run locally with pytest
- [x] Tests run in Docker Compose
- [x] TSR generates from test results

**CI/CD Verification:**
- [ ] GitHub Actions workflow executes
- [ ] Docker Compose starts in CI
- [ ] All tests execute successfully
- [ ] TSR generated and uploaded as artifact
- [ ] Go/no-go decision logic works
- [ ] Claude Code Review provides feedback

**Claude Integration:**
- [ ] Automatic PR review runs
- [ ] @claude mentions work in comments

## Expected Result
Green CI pipeline with successful TSR generation, ready for AWS deployment preparation.

/cc @nsuberi" \
  --base main \
  --head test/verify-ci-pipeline
```

---

### 3.2 Monitor Workflow Execution

**Watch workflow runs:**
```bash
# Check workflow status
gh pr checks

# List workflow runs
gh run list --branch test/verify-ci-pipeline

# Watch specific run in real-time
gh run watch <run-id>

# View detailed logs
gh run view <run-id> --log
```

**Via GitHub UI:**
1. Go to PR page
2. Click "Checks" tab
3. Expand workflow runs
4. Click failed steps to see logs

**Expected workflows to run:**
- `AI Application CI/CD` - Main test pipeline
- `Claude Code Review` - Automatic PR review

---

### 3.3 Debug and Fix Issues Iteratively

**Common Issues and Fixes:**

**Issue: Workflow doesn't trigger**
- **Cause**: Still in wrong location
- **Fix**: Verify moved to `.github/workflows/ai-app-ci.yml` (repo root)
- **Commit**: `git add .github/ && git commit -m "fix: move workflow to correct location"`

**Issue: Docker build fails**
- **Cause**: Missing dependencies or Dockerfile syntax
- **Fix**: Review Dockerfile, test build locally: `docker build -t test ai-testing-resource/`
- **Commit**: Fix and push

**Issue: Service health check timeout**
- **Cause**: Services taking >120s to start
- **Fix**: Increase timeout in workflow line 34, or optimize service startup
- **Commit**: Adjust timeout value

**Issue: Tests fail with API key error**
- **Cause**: Secret not set or incorrect name
- **Symptom**: "ANTHROPIC_API_KEY not set" in logs
- **Fix**: Set secret via `gh secret set ANTHROPIC_API_KEY`

**Issue: TSR generation fails**
- **Cause**: Missing results directory or git unavailable
- **Fix**: Ensure git installed in Dockerfile, verify results/ directory exists
- **Commit**: Update Dockerfile

**Issue: NO-GO decision blocks pipeline**
- **Cause**: Tests failing
- **Symptom**: Workflow fails at "Check Go/No-Go Decision" step
- **Fix**: Review test failures, fix underlying issues
- **Expected**: This is working as designed! Fix tests to get GO decision

**Iteration Process:**
1. Identify failure in GitHub Actions logs
2. Reproduce locally: `cd ai-testing-resource && docker compose -f docker-compose.yml -f docker-compose.ci.yml up`
3. Fix code/configuration
4. Test locally to confirm fix
5. Commit and push: `git add . && git commit -m "fix: ..." && git push`
6. Monitor workflow re-run
7. Repeat until green

---

### 3.4 Test Claude Integration

**Test 1: Automatic PR Review (already triggered)**
- **Trigger**: PR opened (automatic)
- **Expected**: Claude Code Review workflow runs, posts review comment
- **Verify**: Check PR comments for Claude's code review feedback

**Test 2: @claude Mention in PR Comment**
```bash
# Post comment with @claude mention
gh pr comment <pr-number> --body "@claude Please explain the testing strategy and TSR generation process in this codebase."
```

**Expected:**
- `claude.yml` workflow triggers
- Claude reads PR and repo context
- Claude posts reply comment with explanation

**Test 3: Ask Claude for CI/CD Help**
```bash
gh pr comment <pr-number> --body "@claude The workflow is failing at step X. Can you help diagnose the issue?"
```

**Expected:**
- Claude analyzes workflow logs
- Provides diagnostic information
- Suggests fixes

**Success Criteria:**
- Claude Code Review posts automatic review
- @claude mentions trigger responses
- Claude can access PR context, code, and logs

---

### 3.5 Verify TSR Artifact

**Download and inspect TSR:**
```bash
# List artifacts from workflow run
gh run view <run-id> --json artifacts

# Download TSR artifact
gh run download <run-id> -n test-summary-report

# Inspect TSR content
cat ai-testing-resource/tsr.json | python3 -m json.tool | less

# Verify decision and test results
python3 << 'EOF'
import json

with open('ai-testing-resource/tsr.json') as f:
    tsr = json.load(f)

print(f"TSR ID: {tsr['id']}")
print(f"Decision: {tsr['go_no_go_decision']}")
print(f"Reason: {tsr['decision_reason']}")
print(f"\nTest Results:")
for result in tsr['test_results']:
    status = "✓" if result['failed'] == 0 else "✗"
    print(f"  {status} {result['test_type']}: {result['passed']}/{result['total']} passed")

if tsr.get('blocking_issues'):
    print(f"\nBlocking Issues:")
    for issue in tsr['blocking_issues']:
        print(f"  - {issue}")
EOF
```

**Success Criteria:**
- TSR artifact uploaded successfully
- JSON structure valid and complete
- Go/no-go decision accurate
- All test types represented
- Version manifest includes git SHA

---

### 3.6 Verify Deployment Gate Logic

**Test GO decision (normal flow):**
- Keep PR with all tests passing
- Verify workflow completes successfully
- Check that deployment jobs are skipped (not on main branch)

**Test NO-GO decision:**
```bash
# Create branch with intentional failure
git checkout -b test/force-no-go

# Add failing test
cat > ai-testing-resource/tests/unit/test_intentional_failure.py << 'EOF'
"""Intentional failure to test NO-GO decision"""
def test_intentional_failure():
    assert False, "Testing NO-GO decision gate"
EOF

# Commit and push
git add ai-testing-resource/tests/unit/test_intentional_failure.py
git commit -m "test: add intentional failure for NO-GO testing"
git push -u origin test/force-no-go

# Create PR
gh pr create --title "Test: NO-GO Decision" \
  --body "Testing NO-GO decision gate with intentional test failure." \
  --base main --head test/force-no-go
```

**Expected behavior:**
- Workflow fails at "Check Go/No-Go Decision" step
- Error message: "Deployment blocked: NO-GO decision"
- Blocking issues listed in logs
- Deployment jobs don't execute

**Cleanup:**
```bash
gh pr close <pr-number>
git checkout test/verify-ci-pipeline
git branch -D test/force-no-go
git push origin --delete test/force-no-go
```

---

## Phase 4: Achieve Green Pipeline

### 4.1 Full Green Build

**Ensure all issues resolved:**
```bash
# Return to main test branch
git checkout test/verify-ci-pipeline

# Remove any intentional failures
rm -f ai-testing-resource/tests/unit/test_intentional_failure.py

# Verify tests pass locally
cd ai-testing-resource
docker compose -f docker-compose.yml -f docker-compose.ci.yml up

# If all pass, commit any final fixes
git add .
git commit -m "fix: ensure all tests pass in CI" --allow-empty
git push
```

**Monitor until fully green:**
```bash
gh run watch

# Expected output:
# ✓ Checkout repository
# ✓ Set up Docker Buildx
# ✓ Start Docker Compose services
# ✓ Wait for services to be healthy
# ✓ Run tests and generate TSR
# ✓ Upload TSR to API (may skip if no URL)
# ✓ Check Go/No-Go Decision (GO)
# ✓ Upload TSR Artifact
# ✓ Cleanup
```

**Success Criteria:**
- All workflow steps green
- No test failures
- TSR shows GO decision
- Artifact uploaded successfully
- Claude reviews provided feedback
- Pipeline completes in <10 minutes

---

### 4.2 Merge to Main

**Once pipeline is green:**
```bash
# Request approval (optional)
gh pr review <pr-number> --approve --body "CI/CD pipeline validated successfully ✓"

# Merge PR
gh pr merge <pr-number> --squash --delete-branch

# Verify main branch workflow
git checkout main
git pull
gh run list --branch main --limit 1
```

**Post-merge verification:**
- Workflow runs on main branch
- Deployment jobs show as "skipped" (placeholders)
- TSR artifact available

---

## Phase 5: Documentation and Monitoring

### 5.1 Update Documentation

**Verify documentation accuracy:**
- [ ] `ai-testing-resource/README.md` - Commands match implementation
- [ ] `ai-testing-resource/DOCKER_TESTING_GUIDE.md` - CI/CD process documented
- [ ] Workflow triggers documented
- [ ] Claude integration usage documented

**Add CI/CD status badge to README (optional):**
```markdown
[![CI/CD](https://github.com/nsuberi/ai-evals-in-context/actions/workflows/ai-app-ci.yml/badge.svg)](https://github.com/nsuberi/ai-evals-in-context/actions/workflows/ai-app-ci.yml)
```

---

### 5.2 Monitoring Strategy

**Weekly checks:**
```bash
# Review recent workflow runs
gh run list --limit 10

# Check for failures
gh run list --status failure --limit 5
```

**Monthly maintenance:**
- Review GitHub Actions usage (Settings → Billing)
- Update dependencies (requirements.txt, Docker base images)
- Archive old TSR artifacts
- Monitor Anthropic API usage

---

## Success Criteria

### Local Verification ✓
- [x] Tests run in native Python environment
- [x] Tests run in Docker containers
- [x] TSR generates from test results
- [x] JUnit XML format correct
- [x] All test categories execute

### GitHub Actions ✓
- [ ] Workflow in correct location (`.github/workflows/`)
- [ ] Git installed in Docker container
- [ ] ANTHROPIC_API_KEY secret configured
- [ ] Docker Compose starts in CI
- [ ] All tests execute successfully
- [ ] TSR generated and uploaded
- [ ] Go/no-go decision works
- [ ] Deployment gates function correctly

### Claude Integration ✓
- [ ] Automatic PR reviews work
- [ ] @claude mentions trigger responses
- [ ] Claude accesses PR context and code

### Pipeline Health ✓
- [ ] Green build on main branch
- [ ] Completes in <10 minutes
- [ ] No resource exhaustion
- [ ] Artifacts uploaded successfully

---

## Critical Files

| File | Purpose | Changes Needed |
|------|---------|----------------|
| `.github/workflows/ai-app-ci.yml` | Main CI/CD workflow | **MOVE** from `ai-testing-resource/.github/workflows/` to repo root |
| `ai-testing-resource/Dockerfile` | Container image definition | **ADD** `git` to apt-get install (line 9) |
| `ai-testing-resource/docker-compose.ci.yml` | CI-optimized compose config | **OPTIONAL** Remove redundant test execution |
| `ai-testing-resource/scripts/generate_tsr.py` | TSR generation script | No changes (uses GitHub SHA parameter) |
| `ai-testing-resource/.env.docker` | CI environment template | No changes (GitHub injects API key) |
| `.github/workflows/claude.yml` | Claude assistant workflow | No changes needed |
| `.github/workflows/claude-code-review.yml` | Auto PR review workflow | No changes needed |

---

## Verification Checklist

### Prerequisites
- [ ] Docker installed and running
- [ ] Python 3.9+ available
- [ ] ANTHROPIC_API_KEY set locally
- [ ] GitHub CLI (`gh`) installed

### Local Testing
- [ ] Unit tests pass natively
- [ ] Tests pass in Docker
- [ ] TSR generates locally
- [ ] JUnit XML created

### GitHub Setup
- [ ] Workflow moved to `.github/workflows/ai-app-ci.yml`
- [ ] Git added to Dockerfile
- [ ] ANTHROPIC_API_KEY secret set in GitHub

### CI/CD Testing
- [ ] Test PR created
- [ ] Workflow triggers and runs
- [ ] All steps complete successfully
- [ ] TSR artifact downloaded and verified
- [ ] GO decision achieved

### Claude Integration
- [ ] Automatic PR review posted
- [ ] @claude mentions work
- [ ] Claude provides helpful feedback

### Final Validation
- [ ] Green pipeline on test branch
- [ ] PR merged to main
- [ ] Main branch workflow green
- [ ] Documentation updated
- [ ] Ready for AWS/Terraform next phase

---

## Next Steps (Not in This Phase)

After successful verification:
1. **AWS Infrastructure**: Set up AWS account, configure credentials
2. **Terraform Setup**: Write infrastructure as code for deployment
3. **Deployment Pipeline**: Replace placeholder deployment jobs with actual deployment commands
4. **Production Monitoring**: Connect TSR API to production database
5. **Alerting**: Set up notifications for pipeline failures
