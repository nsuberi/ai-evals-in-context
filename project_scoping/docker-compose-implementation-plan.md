# Docker Compose Setup for AI Testing Resource

## Overview
Create a complete Docker Compose environment for local development and CI/CD integration testing, including PostgreSQL database, initialization scripts, test data seeding, and monitoring baseline configuration.

## Current State Analysis

### Existing Infrastructure
- **No Docker setup exists** - greenfield containerization opportunity
- **Phase 2 fully implemented** with TSR database, monitoring, governance portal
- **SQLite default** (sqlite:///tsr.db) but PostgreSQL-ready via SQLAlchemy
- **ChromaDB** uses persistent local storage at `./chroma_db`
- **Flask-SocketIO** for WebSocket monitoring (supports Redis queue)
- **Complete test suite** with fixtures and sample data in `tests/fixtures/`
- **CI/CD pipeline** exists in `.github/workflows/ai-app-ci.yml`

### Key Components to Containerize
1. **Flask API** - Main application with TSR, monitoring, governance
2. **PostgreSQL** - TSR database (test_summary_reports + related tables)
3. **Redis** (Optional) - For distributed WebSocket support
4. **Volume Mounts** - ChromaDB persistence, knowledge base, test data

## Implementation Plan

### 1. Docker Compose Configuration

**File:** `docker-compose.yml` (root directory)

```yaml
services:
  # PostgreSQL database for TSR storage
  postgres:
    image: postgres:15-alpine
    container_name: tsr-postgres
    environment:
      POSTGRES_DB: tsr_db
      POSTGRES_USER: tsr_user
      POSTGRES_PASSWORD: tsr_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U tsr_user -d tsr_db"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - tsr-network

  # Redis for distributed WebSocket support
  redis:
    image: redis:7-alpine
    container_name: tsr-redis
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5
    networks:
      - tsr-network

  # Flask API application
  api:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: tsr-api
    environment:
      # Database
      TSR_DATABASE_URL: postgresql://tsr_user:tsr_password@postgres:5432/tsr_db
      # Flask
      FLASK_DEBUG: "False"
      FLASK_HOST: 0.0.0.0
      FLASK_PORT: 5000
      SECRET_KEY: ${SECRET_KEY:-dev-secret-key-change-in-production}
      # AI Configuration
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      ANTHROPIC_MODEL: claude-sonnet-4-20250514
      EMBEDDING_MODEL: all-MiniLM-L6-v2
      # Storage paths
      CHROMA_PATH: /app/chroma_db
      # Monitoring
      MONITORING_ENABLED: "True"
      MONITORING_WINDOW_MINUTES: 15
      TRACE_RETENTION_HOURS: 24
      SOCKETIO_MESSAGE_QUEUE: redis://redis:6379/0
      # ChromaDB telemetry
      ANONYMIZED_TELEMETRY: "False"
    volumes:
      - ./data:/app/data
      - chroma_data:/app/chroma_db
      - ./scripts:/app/scripts
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/tsr/stats"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - tsr-network
    command: >
      sh -c "
        echo 'Waiting for database...' &&
        python scripts/init_database.py &&
        echo 'Starting Flask application...' &&
        python run.py
      "

volumes:
  postgres_data:
    driver: local
  chroma_data:
    driver: local

networks:
  tsr-network:
    driver: bridge
```

**File:** `docker-compose.ci.yml` (CI/CD override)

```yaml
# Optimized for CI/CD - faster startup, no volumes
services:
  postgres:
    tmpfs:
      - /var/lib/postgresql/data
    environment:
      POSTGRES_HOST_AUTH_METHOD: trust  # Faster startup

  api:
    environment:
      FLASK_DEBUG: "True"
      # Use in-memory ChromaDB for faster tests
      CHROMA_PATH: /tmp/chroma_db
    volumes: []
    command: >
      sh -c "
        python scripts/init_database.py &&
        python scripts/seed_test_data.py &&
        pytest tests/ --junitxml=results/test-results.xml -v
      "
```

### 2. Dockerfile

**File:** `Dockerfile` (root directory)

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create directories for data persistence
RUN mkdir -p /app/chroma_db /app/data/knowledge_base /app/data/traces /app/results

# Expose Flask port
EXPOSE 5000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5000/api/tsr/stats || exit 1

# Default command (can be overridden in docker-compose)
CMD ["python", "run.py"]
```

**File:** `.dockerignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
*.egg-info/
dist/
build/

# Virtual environments
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Data (will be mounted as volumes)
chroma_db/
*.db
*.sqlite

# Git
.git/
.gitignore

# CI/CD
.github/

# Documentation
*.md
!README.md

# Test outputs
.pytest_cache/
.coverage
htmlcov/
results/
```

### 3. Database Initialization Script

**File:** `scripts/init_database.py`

Python script that:
- Waits for PostgreSQL to be ready (retry logic with max_retries)
- Creates TSR database tables using SQLAlchemy
- Checks if tables already exist (avoids recreating)
- Initializes ChromaDB collection
- Loads knowledge base markdown documents
- Handles FORCE_RECREATE_TABLES environment variable

### 4. Test Data Seeding Script

**File:** `scripts/seed_test_data.py`

Python script that:
- Creates 3 sample TSRs representing V1, V2, V3 iterations
- Generates realistic test results with appropriate pass/fail rates
- Creates eval iteration history showing improvement
- Includes sample requirements coverage
- Applies go/no-go decision rules
- Only seeds if database is empty (prevents duplicates)

### 5. Monitoring Baseline Configuration

**File:** `scripts/init_monitoring_baselines.py`

Python script that:
- Loads V3 production traces (if available)
- Calculates baseline metrics (latency, satisfaction)
- Saves baselines to `config/monitoring_baselines.json`
- Initializes anomaly detector with thresholds
- Falls back to recommended defaults if no traces

**File:** `config/monitoring_baselines.json` (Generated by script)

### 6. Environment Configuration

**File:** `.env.docker` (Docker-specific environment)

Contains all environment variables for Docker deployment:
- PostgreSQL connection string
- Flask settings
- Anthropic API key placeholder
- Model configuration
- Storage paths
- Monitoring settings
- ChromaDB telemetry

### 7. Documentation Updates

**File:** `DOCKER_SETUP.md` (New documentation)

Comprehensive guide including:
- Quick start instructions
- Commands for database management
- Logs and debugging
- Configuration options
- Production deployment notes
- Troubleshooting section

### 8. CI/CD Integration Update

**File:** `.github/workflows/ai-app-ci.yml` (Update test-and-evaluate job)

Changes:
- Replace Python setup with Docker Buildx setup
- Start services using docker-compose with CI override
- Run tests inside containers
- Generate TSR inside container
- Extract results for artifacts
- Clean up containers after run

## Critical Files

### New Files to Create
1. `docker-compose.yml` - Main orchestration
2. `docker-compose.ci.yml` - CI/CD override
3. `Dockerfile` - API container image
4. `.dockerignore` - Build optimization
5. `scripts/init_database.py` - Database initialization
6. `scripts/seed_test_data.py` - Test data seeding
7. `scripts/init_monitoring_baselines.py` - Monitoring baseline setup
8. `.env.docker` - Docker environment template
9. `DOCKER_SETUP.md` - Docker documentation
10. `config/monitoring_baselines.json` - Generated baseline config

### Files to Update
1. `.github/workflows/ai-app-ci.yml` - Add Docker Compose steps
2. `README.md` - Add Docker setup section

### Existing Files (No Changes)
- All Python code in `app/`, `tsr/`, `monitoring/`, `viewer/`
- All test files in `tests/`
- `requirements.txt`
- `config.py`

## Verification Steps

After implementation, verify the setup:

### 1. Local Development
```bash
# Start services
docker-compose up -d

# Check health
docker-compose ps
curl http://localhost:5000/api/tsr/stats

# Access web interface
open http://localhost:5000/governance/dashboard
open http://localhost:5000/monitoring/traces
```

### 2. Database Verification
```bash
# Check TSR tables
docker-compose exec postgres psql -U tsr_user -d tsr_db -c "\dt"

# Check seeded data
docker-compose exec api python -c "
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tsr.repository import TSRRepository
from config import TSR_DATABASE_URL
engine = create_engine(TSR_DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
repo = TSRRepository(session)
print(f'Total TSRs: {repo.count()}')
print(f'GO: {repo.count(decision=\"go\")}')
print(f'NO-GO: {repo.count(decision=\"no_go\")}')
"
```

### 3. ChromaDB Verification
```bash
docker-compose exec api python -c "
from app.rag import get_collection
collection = get_collection()
print(f'Documents in knowledge base: {collection.count()}')
"
```

### 4. Monitoring Verification
```bash
# Check baseline configuration
docker-compose exec api cat config/monitoring_baselines.json

# Test anomaly detector
docker-compose exec api python -c "
from monitoring.anomaly import AnomalyDetector
from monitoring.models import AnomalyThresholds
import json
with open('config/monitoring_baselines.json') as f:
    baselines = json.load(f)
detector = AnomalyDetector()
detector.set_baseline(baselines['latency_p95'], baselines['satisfaction_rate'])
print('Anomaly detector initialized successfully')
print(f'Latency threshold: {baselines[\"latency_p95\"] * 1.5}ms')
"
```

### 5. CI/CD Test
```bash
# Run CI workflow locally
docker-compose -f docker-compose.yml -f docker-compose.ci.yml run --rm api

# Should:
# - Initialize database
# - Seed test data
# - Run all tests
# - Generate TSR
# - Exit with code 0 if all pass
```

## Success Criteria

✅ Docker Compose starts all services (postgres, redis, api)
✅ Database tables created automatically on first run
✅ Knowledge base initialized with documents
✅ Test data seeded successfully
✅ Monitoring baselines configured
✅ API accessible at http://localhost:5000
✅ Governance portal renders TSRs
✅ Monitoring dashboard shows baselines
✅ CI/CD workflow runs in Docker
✅ Tests pass in containerized environment
✅ Volumes persist data across restarts

## Notes

- **PostgreSQL** chosen over SQLite for multi-container support
- **Redis** optional but enables distributed WebSocket (production-ready)
- **Health checks** ensure proper startup ordering
- **Volume mounts** separate code (bind) from data (volumes)
- **CI override** uses tmpfs for faster tests
- **Baseline calculation** uses V3 traces (production-ready performance)
- **Seeding** creates 3 sample TSRs matching V1/V2/V3 evolution
- **Production deployment** deferred - will add Terraform for AWS later
