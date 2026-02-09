# Fix CI/CD Flask Crash and Docker Build Optimization

## Problem Summary

Two related issues are affecting the CI/CD pipeline:

1. **Flask Application Crash**: The Flask app crashes immediately in CI (works locally)
2. **Redundant Docker Builds**: Docker image is built twice, causing unnecessary layer exports

## Issue 1: Flask Crash in CI

### Evidence from CI Logs
```
tsr-api  | Seeding complete!
tsr-api  | Starting Flask application...
[Container exits - NO output from run.py whatsoever]
```

### Root Cause Analysis

The crash happens **before** `run.py` prints anything, meaning it fails during Python imports. Key observations:

1. **Scripts work fine**: `init_database.py` and `seed_test_data.py` both use Python and complete successfully
2. **run.py crashes immediately**: No "Initializing knowledge base..." message (first print in `main()`)
3. **Local works, CI fails**: Same docker-compose files but different results

### Most Likely Cause: Docker Image Mismatch

The CI workflow builds an image with `docker buildx build -t tsr-api:latest`, but **docker-compose.yml** has:
```yaml
api:
  build:
    context: .
    dockerfile: Dockerfile
```

This causes `docker compose up` to build a **new image** with name `ai-testing-resource-api` instead of using the pre-built `tsr-api:latest`. The mismatch means:
- The cached/optimized image is never used
- A fresh build happens without the buildx cache
- Potential inconsistencies between builds

### Fix: Use Pre-built Image in CI

**Option A (Recommended)**: Tell docker-compose to use the pre-built image:
```yaml
# docker-compose.ci.yml
api:
  image: ai-testing-resource-api:latest  # Use pre-built image
  build: !reset null  # Remove build section entirely
```

**Option B**: Use `--no-build` flag in CI:
```bash
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build
```

**Option C**: Add image name to docker-compose.yml:
```yaml
api:
  image: ai-testing-resource-api:latest
  build:
    context: .
    dockerfile: Dockerfile
```

---

## Issue 2: Docker Layer Export Optimization

### Current Problem

The CI workflow uses `docker buildx build` which is designed for multi-platform builds and has different caching behavior than regular `docker build`. The `--load` flag forces an export to the local Docker daemon, creating additional layer transfer overhead.

### Current Workflow (Inefficient)
```yaml
- name: Build Docker image with cache
  run: |
    docker buildx build \
      --cache-from type=local,src=/tmp/.buildx-cache \
      --cache-to type=local,dest=/tmp/.buildx-cache-new,mode=max \
      --load \
      -t tsr-api:latest \
      -f Dockerfile .
```

Then `docker compose up` **rebuilds the image again** because docker-compose.yml has a `build:` section.

### Optimized Approach

**Use regular `docker compose build` with buildx for caching:**

```yaml
- name: Build Docker images
  working-directory: ./ai-testing-resource
  run: |
    # Build image using docker compose (respects image names)
    docker compose build --no-cache=false

- name: Start services (no rebuild)
  working-directory: ./ai-testing-resource
  run: |
    docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build
```

Or if caching is needed, use `docker compose build` with the proper image reference.

---

## Implementation Plan

### Phase 1: Fix Docker Compose Image Reference

**File: `ai-testing-resource/docker-compose.ci.yml`**

Add image name and disable build:
```yaml
services:
  api:
    image: ai-testing-resource-api:latest
    # Remove or override build section
```

### Phase 2: Simplify CI Workflow

**File: `.github/workflows/ai-app-ci.yml`**

Replace the complex buildx approach with simpler docker compose build:

```yaml
- name: Build Docker images
  working-directory: ./ai-testing-resource
  run: |
    # Use docker compose build - simpler, respects image names
    docker compose build

- name: Start Docker Compose services
  working-directory: ./ai-testing-resource
  run: |
    cp .env.docker .env
    echo "ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}" >> .env
    # --no-build prevents rebuilding since we already built
    docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build
```

### Phase 3: Add Debug Output to run.py

To diagnose any remaining issues, add early debug output:

**File: `ai-testing-resource/run.py`**

```python
#!/usr/bin/env python
"""Run the AI Testing Resource application"""

import sys
print("run.py: Starting...", flush=True)  # Debug output

import os
from pathlib import Path
print("run.py: Basic imports done", flush=True)

sys.path.insert(0, str(Path(__file__).parent))

try:
    from dotenv import load_dotenv
    print("run.py: dotenv imported", flush=True)
except Exception as e:
    print(f"run.py: dotenv import failed: {e}", flush=True)
    sys.exit(1)

# ... rest of imports with similar debug output
```

---

## Files to Modify

1. **`ai-testing-resource/docker-compose.ci.yml`** - Add image name, remove redundant build
2. **`.github/workflows/ai-app-ci.yml`** - Simplify build process, use `--no-build`
3. **`ai-testing-resource/run.py`** - Add debug output for diagnosis

---

## Verification Steps

### Local Testing
```bash
cd ai-testing-resource
docker compose down -v
docker compose build
docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d --no-build
docker compose ps  # All 3 should be healthy
curl http://localhost:5001/api/tsr/stats  # Should return JSON
```

### CI Testing
1. Push changes to branch
2. Monitor GitHub Actions run
3. Expected results:
   - Build step completes faster (no duplicate builds)
   - All 3 containers become healthy
   - Tests run successfully

---

## Success Criteria

- [ ] Flask app starts without crashing in CI
- [ ] Docker image built only once per CI run
- [ ] No unnecessary layer exports
- [ ] Health check passes within 60 seconds
- [ ] All tests run successfully

---

## Rollback Plan

If the changes don't work:

1. Revert docker-compose.ci.yml changes
2. Keep the `--no-build` flag approach in CI workflow
3. Add more debug output to identify the exact failure point
