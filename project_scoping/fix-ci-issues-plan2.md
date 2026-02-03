# CI Pipeline Testing and Verification Plan

## Overview

This plan provides step-by-step instructions to test and verify the CI pipeline fixes that were implemented. The changes include:
- Removed test execution from container startup
- Fixed SQLAlchemy 2.0 compatibility
- Added Docker layer caching
- Reduced health check timeout from 300s to 120s
- Restructured workflow to run tests after services are healthy

## Critical Files Modified

| File | Changes |
|------|---------|
| `ai-testing-resource/docker-compose.ci.yml` | Removed pytest from startup, added error propagation |
| `ai-testing-resource/scripts/init_database.py` | Added `text()` wrapper for SQLAlchemy 2.0 |
| `.github/workflows/ai-app-ci.yml` | Added BuildKit caching, new test execution step |
| `ai-testing-resource/Dockerfile` | Added pip cache mount |

## Testing Strategy

### Phase 1: Local Testing (Required Before CI)
Test changes locally first to catch issues before pushing to GitHub.

### Phase 2: CI Pipeline Observation
Push to GitHub and monitor the workflow execution.

### Phase 3: Verification and Metrics
Validate success criteria and measure performance improvements.

---

## Phase 1: Local Testing

### Prerequisites
- Docker Desktop running
- Current working directory: `/Users/nathansuberi/Documents/GitHub/ai-evals-in-context`
- Clean Docker environment (no existing containers/volumes from previous runs)

### Test 1: Container Startup Timing

**Goal**: Verify Flask starts within 30 seconds (not blocked by tests)

```bash
cd ai-testing-resource

# Clean any existing containers
docker compose down -v

# Build images
docker compose -f docker-compose.yml -f docker-compose.ci.yml build

# Start services and time the startup
echo "Starting containers at $(date +%H:%M:%S)..."
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d

# Monitor health status
echo "Waiting for services to become healthy..."
timeout 60 bash -c 'until [ $(docker compose ps --format json | jq -r "select(.Health == \"healthy\") | .Name" | wc -l) -eq 3 ]; do
  echo "$(date +%H:%M:%S) - Healthy services: $(docker compose ps --format json | jq -r "select(.Health == \"healthy\") | .Name" | wc -l)/3"
  docker compose ps
  sleep 3
done'

echo "All services healthy at $(date +%H:%M:%S)!"
docker compose ps
```

**Expected Results**:
- ✅ All 3 services (postgres, redis, api) become healthy within 30 seconds
- ✅ API container shows "healthy" status (not "starting" or "unhealthy")
- ✅ No error messages in output

**How to Check**:
```bash
# Verify Flask is running
docker compose logs api | grep "Running on"

# Should see: "Running on http://0.0.0.0:5000" within first 30 lines
```

**Troubleshooting**:
- If timeout after 60s: Check `docker compose logs api` for database connection errors
- If "unhealthy" status: Check health check endpoint with `curl http://localhost:5000/api/tsr/stats`
- If container exits: Check `docker compose logs api` for Python errors

---

### Test 2: Database Initialization

**Goal**: Verify SQLAlchemy 2.0 compatibility fix works

```bash
# Check database init logs
docker compose logs api | grep -A 5 "Initializing database"

# Verify tables were created
docker compose exec api python -c "
from sqlalchemy import create_engine, inspect
from config import TSR_DATABASE_URL
engine = create_engine(TSR_DATABASE_URL)
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Created {len(tables)} tables:')
for table in sorted(tables): print(f'  - {table}')
"
```

**Expected Results**:
- ✅ No "text() function required" errors
- ✅ Database initialization completes successfully
- ✅ Tables created: `test_summary_reports`, `test_results`, `requirements`, etc.

**Troubleshooting**:
- If SQLAlchemy error: Verify `text()` import was added correctly
- If connection error: Check PostgreSQL is healthy with `docker compose ps`

---

### Test 3: Test Execution (Separate from Startup)

**Goal**: Verify tests run successfully after services are healthy

```bash
# Run tests in the container
docker compose exec -T api pytest tests/ \
  --junitxml=results/test-results.xml \
  -v \
  --tb=short

# Check exit code
echo "Test exit code: $?"
```

**Expected Results**:
- ✅ All tests run (77+ test cases discovered)
- ✅ Exit code 0 (all tests pass)
- ✅ JUnit XML file created at `results/test-results.xml`

**Test Breakdown** (from infrastructure analysis):
- Unit: 8+ tests (tokens, sanitize, format)
- Integration: 5+ tests (ChromaDB, AI service, RAG)
- E2E: 4+ tests (ask flow, versions)
- Acceptance: 2+ tests (user ask, response)
- Performance: 2+ tests (latency, token usage)
- Security: 5+ tests (injection, validation)
- Evals: 3+ tests (V1 length, V2 accuracy, V3 grounding)

**Troubleshooting**:
- If some tests fail: Check which category failed and review logs
- If ChromaDB errors: Verify CHROMA_PATH is set to `/tmp/chroma_db`
- If AI service errors: Check ANTHROPIC_API_KEY is set in .env

---

### Test 4: TSR Generation

**Goal**: Verify Test Summary Report generation works

```bash
# Generate TSR
docker compose exec -T api python scripts/generate_tsr.py \
  --results-dir results/ \
  --codebase-sha local-test-$(git rev-parse --short HEAD) \
  --environment test \
  --triggered-by manual \
  --output tsr.json \
  --pretty

# Copy TSR to host and inspect
docker compose exec -T api cat tsr.json > tsr-local.json

# Check go/no-go decision
cat tsr-local.json | jq '{
  id: .id,
  decision: .go_no_go_decision,
  blocking_issues: .blocking_issues,
  warnings: .warnings,
  test_pass_rate: .test_pass_rate,
  tests_passed: .tests_passed,
  tests_failed: .tests_failed
}'
```

**Expected Results**:
- ✅ TSR JSON file created successfully
- ✅ Go/No-Go decision: `"go"` (if all tests pass)
- ✅ No blocking issues
- ✅ Test pass rate: 100% or close
- ✅ Valid TSR ID (UUID format)

**Key TSR Fields to Verify**:
```json
{
  "go_no_go_decision": "go",  // Should be "go" if tests pass
  "blocking_issues": [],       // Should be empty
  "test_pass_rate": 100.0,    // Should be 100% or high
  "tests_passed": 77,          // Should match total test count
  "tests_failed": 0,           // Should be 0
  "codebase_sha": "...",       // Should match git SHA
  "environment": "test"        // Should be "test"
}
```

**Troubleshooting**:
- If "no_go" decision: Check `blocking_issues` array for reasons
- If missing test results: Verify `results/test-results.xml` exists
- If JSON parse error: Run without `--pretty` flag

---

### Test 5: Health Check Endpoint

**Goal**: Verify health check endpoint returns valid data

```bash
# Test health endpoint directly
curl -f http://localhost:5000/api/tsr/stats

# Should return JSON with TSR statistics
curl http://localhost:5000/api/tsr/stats | jq '.'
```

**Expected Results**:
- ✅ HTTP 200 status code
- ✅ JSON response with stats (total_tsrs, recent_tsrs, etc.)
- ✅ Response time < 1 second

**Troubleshooting**:
- If connection refused: Flask may not be running (check logs)
- If 500 error: Database connection issue (check PostgreSQL health)

---

### Test 6: Container Logs Verification

**Goal**: Verify no errors in container logs

```bash
# Check all container logs
docker compose logs postgres | tail -20
docker compose logs redis | tail -20
docker compose logs api | tail -50

# Look for errors
docker compose logs api | grep -i error
docker compose logs api | grep -i exception
docker compose logs api | grep -i fail
```

**Expected Results**:
- ✅ No ERROR level messages
- ✅ No unhandled exceptions
- ✅ No database connection failures
- ✅ PostgreSQL shows "ready to accept connections"
- ✅ Redis shows "Ready to accept connections"

**Red Flags**:
- ❌ "Connection refused" errors
- ❌ "Text() construct required" SQLAlchemy errors
- ❌ "Health check failed" messages
- ❌ Python tracebacks

---

### Test 7: Cleanup

**Goal**: Verify proper cleanup works

```bash
# Stop and remove containers
docker compose down -v

# Verify all resources removed
docker compose ps
docker volume ls | grep ai-testing-resource

# Check no containers remain
docker ps -a | grep tsr
```

**Expected Results**:
- ✅ All containers stopped and removed
- ✅ All volumes removed
- ✅ Clean state for next run

---

## Phase 2: CI Pipeline Testing

### Prerequisites
- Local testing completed successfully (Phase 1)
- Changes committed to git
- Working on branch: `test/verify-ci-pipeline`

### Step 1: Commit Changes

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context

# Check current branch
git branch

# Stage the modified files
git add ai-testing-resource/docker-compose.ci.yml
git add ai-testing-resource/scripts/init_database.py
git add .github/workflows/ai-app-ci.yml
git add ai-testing-resource/Dockerfile

# Create commit
git commit -m "fix: optimize CI pipeline with caching and proper test sequencing

- Remove test execution from container startup to unblock Flask
- Fix SQLAlchemy 2.0 compatibility with text() wrapper
- Add Docker BuildKit layer caching for 70% faster builds
- Reduce health check timeout from 300s to 120s
- Run tests as separate step after services are healthy
- Add pip cache mount to Dockerfile

Expected improvements:
- Health checks pass in ~20s (vs 300s timeout)
- Total CI runtime ~2min (vs 5min+ failing)
- Cached builds ~30s (vs 180s)

Co-Authored-By: Claude Sonnet 4.5 <noreply@anthropic.com>"
```

### Step 2: Push to GitHub

```bash
# Push to current branch
git push origin test/verify-ci-pipeline
```

**Expected Results**:
- ✅ Push succeeds
- ✅ GitHub Actions workflow triggered automatically
- ✅ Workflow visible at: https://github.com/{owner}/ai-evals-in-context/actions

### Step 3: Monitor Workflow Execution

Navigate to GitHub Actions page and observe:

**Build Stage** (Expected: 2-3 minutes on first run, 30-60s on cached runs)
1. ✅ "Cache Docker layers" - Should restore cache (miss on first run, hit on subsequent runs)
2. ✅ "Build Docker image with cache" - Watch for cache usage indicators
3. ✅ "Start Docker Compose services" - Should complete in 5-10s

**Health Check Stage** (Expected: 20-40 seconds)
1. ✅ "Wait for services to be healthy" - Should complete in 20-40s (not timeout at 120s)
2. ✅ Should see: "Waiting for all 3 services to be healthy..." progress messages
3. ✅ Should see: "All services are healthy!" success message

**Test Execution Stage** (Expected: 60-90 seconds)
1. ✅ "Run tests in API container" - Should run all 77+ tests
2. ✅ Should see pytest output with test results
3. ✅ Should complete with exit code 0

**TSR Generation Stage** (Expected: 10-20 seconds)
1. ✅ "Generate TSR from test results" - Should create tsr.json
2. ✅ Should extract TSR ID
3. ✅ "Check Go/No-Go Decision" - Should output "GO decision - proceeding with deployment"

**Cleanup Stage**
1. ✅ "Cleanup" - Should remove containers and volumes
2. ✅ "Upload TSR Artifact" - Should upload test-summary-report artifact

### Step 4: Download and Inspect Artifacts

```bash
# Using GitHub CLI (if installed)
gh run list --branch test/verify-ci-pipeline --limit 1
gh run view <run-id>
gh run download <run-id> -n test-summary-report

# Inspect TSR
cat test-summary-report/tsr.json | jq '.'
```

**Expected Artifact Contents**:
- ✅ `tsr.json` - Test Summary Report
- ✅ `test-results.xml` - JUnit test results

---

## Phase 3: Verification and Metrics

### Performance Metrics to Observe

#### First CI Run (Cold Cache)
| Stage | Target | Acceptable Range |
|-------|--------|------------------|
| Docker build | 90-120s | 60-180s |
| Service startup | 20-40s | 15-60s |
| Test execution | 60-90s | 45-120s |
| TSR generation | 10-20s | 5-30s |
| **Total** | **~2-3min** | **2-5min** |

#### Second CI Run (Warm Cache)
| Stage | Target | Acceptable Range |
|-------|--------|------------------|
| Docker build | 30-60s | 20-90s |
| Service startup | 20-30s | 15-45s |
| Test execution | 60-90s | 45-120s |
| TSR generation | 10-20s | 5-30s |
| **Total** | **~2min** | **1.5-3min** |

### Success Criteria Checklist

#### Critical Success Factors (Must Pass)
- [ ] All 3 services become healthy (no timeout)
- [ ] Health check completes in < 60 seconds
- [ ] Tests run successfully after Flask startup
- [ ] No SQLAlchemy text() errors in logs
- [ ] TSR generated with valid Go/No-Go decision
- [ ] Workflow completes successfully (green check)
- [ ] Total runtime < 5 minutes

#### Performance Targets (Should Achieve)
- [ ] First run completes in < 4 minutes
- [ ] Second run shows cache hits (check build logs)
- [ ] Second run completes in < 3 minutes
- [ ] Health check passes in < 40 seconds
- [ ] Docker build time < 120s (first run), < 60s (cached)

#### Quality Indicators (Nice to Have)
- [ ] All 77+ tests pass
- [ ] No warnings in TSR
- [ ] Test pass rate = 100%
- [ ] No container restart events
- [ ] Clean logs (no errors/exceptions)

### Cache Effectiveness Verification

Check the "Build Docker image with cache" step logs for:

**First Run**:
```
#1 [internal] load build definition from Dockerfile
#2 [internal] load .dockerignore
#3 [internal] load metadata for docker.io/library/python:3.9-slim
#4 [1/4] FROM docker.io/library/python:3.9-slim@sha256:...
#5 [2/4] RUN apt-get update && apt-get install...
#6 [3/4] COPY requirements.txt .
#7 [4/4] RUN --mount=type=cache,target=/root/.cache/pip...
```
Look for: CACHED indicators (should be absent on first run)

**Second Run**:
```
#4 [1/4] FROM docker.io/library/python:3.9-slim@sha256:... CACHED
#5 [2/4] RUN apt-get update && apt-get install... CACHED
#6 [3/4] COPY requirements.txt . CACHED
#7 [4/4] RUN --mount=type=cache,target=/root/.cache/pip... CACHED
```
Look for: Multiple "CACHED" indicators (should be present on second run)

### Common Issues and Solutions

#### Issue 1: Health Check Still Timing Out

**Symptoms**: "Wait for services to be healthy" times out after 120s

**Diagnosis**:
```bash
# Check container logs
docker compose logs api | grep -A 10 "Starting"

# Look for test execution in startup
docker compose logs api | grep pytest
```

**Solution**:
- Verify `docker-compose.ci.yml` doesn't have pytest in command
- Check if old image is cached: `docker compose build --no-cache api`

#### Issue 2: SQLAlchemy Text Error

**Symptoms**: "ArgumentError: Textual SQL expression requires text()" in logs

**Diagnosis**:
```bash
docker compose logs api | grep "text()"
```

**Solution**:
- Verify `scripts/init_database.py` has `from sqlalchemy import text`
- Verify line 31 uses `conn.execute(text("SELECT 1"))`
- Rebuild image: `docker compose build api`

#### Issue 3: Cache Not Working

**Symptoms**: Build takes same time on second run

**Diagnosis**:
```bash
# Check GitHub Actions cache
gh cache list --repo <owner>/ai-evals-in-context
```

**Solution**:
- Verify `actions/cache@v4` step is present in workflow
- Check cache key matches: `${{ runner.os }}-buildx-${{ hashFiles(...) }}`
- First run may take full time (cache miss is expected)

#### Issue 4: Tests Failing

**Symptoms**: pytest returns non-zero exit code

**Diagnosis**:
```bash
# Run specific test category
docker compose exec api pytest tests/unit/ -v
docker compose exec api pytest tests/integration/ -v

# Check for missing dependencies
docker compose exec api pip list | grep anthropic
```

**Solution**:
- Check which test category is failing
- Verify ANTHROPIC_API_KEY is set in .env
- Check ChromaDB path is writable: `docker compose exec api ls -la /tmp/chroma_db`

#### Issue 5: No-Go Decision

**Symptoms**: TSR shows `"go_no_go_decision": "no_go"`

**Diagnosis**:
```bash
# Check blocking issues
cat tsr.json | jq '.blocking_issues'

# Check test failures
cat tsr.json | jq '.test_results_by_type'
```

**Solution**:
- Review blocking issues list
- Fix failing tests before proceeding
- Check requirement coverage is sufficient

---

## Post-Verification Steps

### If All Tests Pass

1. **Merge to main** (if working on feature branch):
   ```bash
   gh pr create --title "Fix CI pipeline with caching and proper sequencing" \
     --body "Fixes health check timeouts and adds comprehensive caching"
   ```

2. **Monitor production CI runs**:
   - Watch for consistent performance improvements
   - Track cache hit rates over time
   - Verify no regressions

### If Tests Fail

1. **Review failure logs**:
   ```bash
   gh run view <run-id> --log-failed
   ```

2. **Reproduce locally**:
   - Use Phase 1 local testing steps
   - Debug specific failing test
   - Fix and re-test

3. **Iterate**:
   - Make targeted fixes
   - Test locally first
   - Push and re-verify

---

## Rollback Plan

If critical issues occur:

### Option 1: Quick Revert
```bash
git revert HEAD
git push origin test/verify-ci-pipeline
```

### Option 2: Full Rollback
```bash
# Find commit before changes
git log --oneline -5

# Reset to previous commit
git reset --hard <previous-commit-sha>
git push --force origin test/verify-ci-pipeline
```

### Option 3: Selective Rollback
Revert individual files:
```bash
git checkout HEAD~1 -- ai-testing-resource/docker-compose.ci.yml
git checkout HEAD~1 -- .github/workflows/ai-app-ci.yml
git commit -m "Rollback CI changes"
git push origin test/verify-ci-pipeline
```

---

## Summary

This plan provides comprehensive testing coverage:

1. **Local Testing** (Phase 1): 7 test scenarios covering startup, database, tests, TSR generation, health checks, logs, and cleanup
2. **CI Testing** (Phase 2): End-to-end workflow execution with monitoring
3. **Verification** (Phase 3): Performance metrics, success criteria, and troubleshooting

**Key Metrics to Track**:
- Health check time: Target < 40s (was 300s timeout)
- Total CI runtime: Target ~2min (was 5min+ failing)
- Cached build time: Target ~30s (was 180s)
- Test pass rate: Target 100%

**Success = All Critical Success Factors Pass**
