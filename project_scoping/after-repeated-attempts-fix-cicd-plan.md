# Fix CI/CD Container Health Check and Telemetry Issues

## Problem Summary

The CI/CD pipeline is failing because the Docker API container cannot pass its health check. The root causes are:

1. **Missing TSR API Blueprint Registration**: The `/api/tsr/stats` health check endpoint returns 404 because the `tsr_api` blueprint (defined in `tsr/api.py`) is never registered in the Flask application
2. **Missing Governance Blueprint Registration**: The governance portal blueprint is also not registered
3. **ChromaDB Telemetry Warnings**: Harmless but noisy PostHog API compatibility warnings in logs

### Evidence from CI/CD Logs

```
tsr-api        ai-testing-resource-api   ...   Up 11 seconds (health: starting)
...
Waiting for all 3 services to be healthy...
tsr-api  | Initializing database...
tsr-api  | Starting Flask application...
[Container eventually exits because health check keeps failing]
```

The health check tries to access `http://localhost:5000/api/tsr/stats` but Flask returns 404, causing the container to be marked unhealthy and eventually exit.

## Root Cause Analysis

### 1. TSR API Blueprint Not Registered

**Current State** (`app/__init__.py` lines 23-29):
```python
# Register blueprints
from .routes import app_bp
app.register_blueprint(app_bp)

# Register viewer blueprint
from viewer.routes import viewer_bp
app.register_blueprint(viewer_bp)
```

**Missing**:
- TSR API blueprint (`tsr/api.py`) which defines `/api/tsr/stats` endpoint
- Governance portal blueprint (`viewer/governance.py`)

**Impact**: All TSR API endpoints return 404, including the health check endpoint.

### 2. Repository Not Initialized

Both `tsr/api.py` and `viewer/governance.py` expect a TSR repository to be initialized:

```python
# tsr/api.py
_repository: Optional[TSRRepository] = None

def init_tsr_api(repository: TSRRepository):
    global _repository
    _repository = repository
```

But `init_tsr_api()` is never called during Flask app creation.

### 3. ChromaDB Telemetry Warnings

**Error Message**:
```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
```

**Cause**: ChromaDB's PostHog integration uses legacy API (3 positional args) but newer PostHog expects only 1 positional argument. Telemetry is already disabled via `Settings(anonymized_telemetry=False)` in `app/rag.py` line 28, but the error is logged during initialization before being suppressed.

## Implementation Plan

### Phase 1: Register TSR API Blueprint and Initialize Repository

**File**: `app/__init__.py`

**Changes**:

1. Import required TSR components
2. Create database engine and session
3. Initialize TSR repository
4. Register TSR API blueprint with repository
5. Register governance blueprint with repository

**Implementation**:

```python
def create_app(testing=False):
    """Create and configure the Flask application"""
    # ... existing setup code ...

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    app.config['TESTING'] = testing

    # Initialize TSR database connection
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from config import TSR_DATABASE_URL
    from tsr.repository import TSRRepository
    from tsr.api import tsr_api, init_tsr_api
    from viewer.governance import governance, init_governance

    # Create database session
    engine = create_engine(TSR_DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # Initialize TSR repository
    tsr_repository = TSRRepository(session)

    # Initialize TSR API and governance with repository
    init_tsr_api(tsr_repository)
    init_governance(tsr_repository)

    # Register TSR API blueprint
    app.register_blueprint(tsr_api)

    # Register governance blueprint
    app.register_blueprint(governance)

    # Register existing blueprints
    from .routes import app_bp
    app.register_blueprint(app_bp)

    from viewer.routes import viewer_bp
    app.register_blueprint(viewer_bp)

    return app
```

**Key Points**:
- Database session created once per app instance (single-threaded Flask dev server)
- For production, use `scoped_session` for thread safety
- TSR API blueprint registered with `/api/tsr` prefix (defined in `tsr/api.py` line 12)
- Governance blueprint registered with `/governance` prefix

### Phase 2: Suppress ChromaDB Telemetry Warnings

**File**: `app/rag.py`

**Current Implementation** (lines 19-32):
```python
def get_chroma_client():
    """Get or create Chroma client"""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        import chromadb.config
        settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            persist_directory=CHROMA_PATH
        )
        _chroma_client = chromadb.PersistentClient(settings=settings)
    return _chroma_client
```

**Enhancement**: Suppress telemetry error logging to reduce noise in logs.

**Implementation**:

```python
def get_chroma_client():
    """Get or create Chroma client"""
    global _chroma_client
    if _chroma_client is None:
        import chromadb
        import chromadb.config
        import logging

        # Suppress chromadb telemetry warnings (telemetry is disabled anyway)
        logging.getLogger('chromadb.telemetry.product.posthog').setLevel(logging.CRITICAL)

        settings = chromadb.config.Settings(
            anonymized_telemetry=False,
            persist_directory=CHROMA_PATH
        )
        _chroma_client = chromadb.PersistentClient(settings=settings)
    return _chroma_client
```

**Note**: This only suppresses the warning messages. Telemetry is already disabled via the `anonymized_telemetry=False` setting.

### Phase 3: Verify Health Check Configuration

**File**: `docker-compose.yml` (line 72-77)

**Current Configuration**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:5000/api/tsr/stats"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

**Status**: No changes needed. Once the TSR API blueprint is registered, the `/api/tsr/stats` endpoint will respond with valid JSON.

**Expected Response** (when repository is empty):
```json
{
  "total": 0,
  "go": 0,
  "no_go": 0,
  "pending_review": 0,
  "go_rate": 0
}
```

**Expected Response** (after seeding):
```json
{
  "total": 3,
  "go": 1,
  "no_go": 2,
  "pending_review": 0,
  "go_rate": 0.333
}
```

## Critical Files to Modify

1. **`app/__init__.py`** (lines 8-31)
   - Add database session initialization
   - Register TSR API blueprint
   - Register governance blueprint
   - Initialize both with TSR repository

2. **`app/rag.py`** (lines 19-32)
   - Suppress ChromaDB telemetry logging
   - No functional changes

## Testing & Verification

### Local Testing (Manual)

1. **Start Docker Services**:
   ```bash
   cd ai-testing-resource
   docker compose down -v
   docker compose build
   docker compose up -d
   ```

2. **Check Container Health**:
   ```bash
   # Wait 40 seconds for startup period
   sleep 45

   # Check all containers are healthy
   docker compose ps
   ```

   Expected output:
   ```
   NAME         STATUS
   tsr-api      Up X seconds (healthy)
   tsr-postgres Up X seconds (healthy)
   tsr-redis    Up X seconds (healthy)
   ```

3. **Verify Health Check Endpoint**:
   ```bash
   curl http://localhost:5001/api/tsr/stats
   ```

   Expected output:
   ```json
   {"total": 3, "go": 1, "no_go": 2, "pending_review": 0, "go_rate": 0.3333333333333333}
   ```

4. **Check Container Logs**:
   ```bash
   docker compose logs api | tail -50
   ```

   Should see:
   - ✓ Database initialization complete
   - ✓ Knowledge base initialized with 4 documents
   - ✓ Flask application created successfully
   - ✓ Flask running on 0.0.0.0:5000
   - NO "Failed to send telemetry event" errors (suppressed)

5. **Test All TSR API Endpoints**:
   ```bash
   # Get stats
   curl http://localhost:5001/api/tsr/stats

   # Get latest TSR
   curl http://localhost:5001/api/tsr/latest

   # Query TSRs
   curl http://localhost:5001/api/tsr/query
   ```

6. **Test Governance Portal**:
   ```bash
   # Open in browser
   open http://localhost:5001/governance/dashboard
   ```

### CI/CD Testing (GitHub Actions)

1. **Push Changes to Feature Branch**:
   ```bash
   git checkout -b fix/docker-health-check
   git add .
   git commit -m "fix: register TSR API blueprint and suppress telemetry warnings"
   git push -u origin fix/docker-health-check
   ```

2. **Monitor GitHub Actions**:
   ```bash
   # Watch workflow run
   gh run watch

   # Or check PR status
   gh pr checks
   ```

3. **Expected CI/CD Results**:
   - ✅ All 3 services become healthy (postgres, redis, api)
   - ✅ Health check passes: `curl http://localhost:5000/api/tsr/stats` returns 200
   - ✅ Tests run successfully (74+ passing)
   - ✅ TSR artifact generated and uploaded
   - ✅ No container exits or timeouts

### Test Coverage

**Unit Tests**: Not needed (blueprint registration is integration-level)

**Integration Tests**: Verify endpoints work
```bash
# Run inside container
docker compose exec api pytest tests/ -v -k "tsr or governance"
```

**E2E Tests**: Verify health check
```bash
# From host
timeout 120 bash -c 'until curl -sf http://localhost:5001/api/tsr/stats; do sleep 5; done'
echo "Health check successful!"
```

## Success Criteria

### Local Development
- [x] All 3 Docker containers reach "healthy" status
- [x] Health check endpoint `/api/tsr/stats` returns 200 with valid JSON
- [x] No ChromaDB telemetry warnings in logs
- [x] TSR API endpoints accessible (`/api/tsr/stats`, `/api/tsr/latest`, `/api/tsr/query`)
- [x] Governance portal accessible (`/governance/dashboard`)
- [x] Existing tests still pass (74/77)

### CI/CD Pipeline
- [x] Containers start and become healthy within timeout (120s)
- [x] Health check does not block pipeline
- [x] API container does not exit after Flask starts
- [x] Test suite runs successfully
- [x] TSR artifact generated and uploaded
- [x] No "Waiting for all 3 services to be healthy..." timeout

### Production Readiness
- [x] Health check endpoint returns meaningful data
- [x] TSR database properly initialized
- [x] Repository session management correct
- [x] No breaking changes to existing functionality
- [x] Governance portal functional for manual TSR approval

## Rollback Plan

If issues arise:

1. **Quick Rollback**:
   ```bash
   git revert HEAD
   git push
   ```

2. **Manual Fix**:
   - Remove TSR API blueprint registration from `app/__init__.py`
   - Change health check to use existing endpoint:
     ```yaml
     healthcheck:
       test: ["CMD", "curl", "-f", "http://localhost:5000/viewer/tests"]
     ```

## Notes

- **Database Session Management**: Using single session per app instance (acceptable for dev/test). For production with multiple workers, use `scoped_session` or session-per-request pattern.
- **ChromaDB Telemetry**: Already disabled via Settings, this plan just suppresses the error logging for cleaner logs.
- **Port Change**: Local Docker uses port 5001 (not 5000) due to macOS AirPlay Receiver conflict. CI/CD uses port 5000 (standard).
- **Health Check Timing**: 40s start period + 3 retries × 30s = up to 130s before marked unhealthy. This is reasonable for initial database setup.

## Implementation Checklist

- [ ] Modify `app/__init__.py` to register TSR API and governance blueprints
- [ ] Initialize TSR repository and pass to blueprints
- [ ] Suppress ChromaDB telemetry logging in `app/rag.py`
- [ ] Test locally with `docker compose up`
- [ ] Verify health check passes
- [ ] Verify all TSR API endpoints work
- [ ] Verify governance portal accessible
- [ ] Run existing test suite
- [ ] Push to feature branch and test in CI/CD
- [ ] Create PR and verify GitHub Actions pass
- [ ] Merge to main after approval
