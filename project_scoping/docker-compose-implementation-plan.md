# Docker Compose Setup Refinement for AI Testing Resource

## Overview
Refine the Docker Compose implementation with:
1. **Docker Compose V2 syntax** - Update all `docker-compose` to `docker compose`
2. **Local testing with artifacts** - Run tests locally and generate verification artifacts
3. **GitHub PR integration** - Document how to use Claude to monitor GitHub Actions
4. **Feature branch testing** - Ensure tests run on all branches before merging to main

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

```python
#!/usr/bin/env python3
"""
Initialize TSR database tables and ChromaDB knowledge base
Run this before starting the application for the first time
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ProgrammingError
import time

from tsr.database import create_tables, drop_tables
from app.rag import initialize_knowledge_base, get_chroma_client
from config import TSR_DATABASE_URL, KNOWLEDGE_BASE_DIR, CHROMA_PATH


def wait_for_database(max_retries=30, retry_interval=2):
    """Wait for database to be ready"""
    print(f"Waiting for database at {TSR_DATABASE_URL}...")

    for attempt in range(max_retries):
        try:
            engine = create_engine(TSR_DATABASE_URL)
            with engine.connect() as conn:
                conn.execute("SELECT 1")
            print("✓ Database is ready!")
            return engine
        except OperationalError as e:
            if attempt < max_retries - 1:
                print(f"  Database not ready (attempt {attempt + 1}/{max_retries}), retrying...")
                time.sleep(retry_interval)
            else:
                print(f"✗ Database connection failed after {max_retries} attempts")
                raise


def initialize_tsr_database():
    """Create TSR database tables"""
    print("\n=== Initializing TSR Database ===")

    try:
        engine = wait_for_database()

        # Check if tables already exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()

        if 'test_summary_reports' in existing_tables:
            print("⚠ TSR tables already exist")
            response = os.getenv('FORCE_RECREATE_TABLES', 'no').lower()

            if response == 'yes':
                print("  Dropping existing tables...")
                drop_tables(engine)
                print("  Creating fresh tables...")
                create_tables(engine)
                print("✓ TSR tables recreated")
            else:
                print("  Skipping table creation (set FORCE_RECREATE_TABLES=yes to recreate)")
        else:
            print("Creating TSR tables...")
            create_tables(engine)
            print("✓ TSR tables created successfully")

            # Print table summary
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            print(f"\nCreated {len(tables)} tables:")
            for table in sorted(tables):
                print(f"  - {table}")

    except Exception as e:
        print(f"✗ Failed to initialize TSR database: {e}")
        raise


def initialize_chroma_database():
    """Initialize ChromaDB and load knowledge base"""
    print("\n=== Initializing ChromaDB Knowledge Base ===")

    try:
        # Ensure chroma directory exists
        os.makedirs(CHROMA_PATH, exist_ok=True)
        print(f"ChromaDB path: {CHROMA_PATH}")

        # Initialize client
        client = get_chroma_client()

        # Check if collection exists
        collections = [c.name for c in client.list_collections()]

        if 'acme_knowledge_base' in collections:
            print("⚠ Knowledge base collection already exists")

            # Check document count
            collection = client.get_collection("acme_knowledge_base")
            count = collection.count()
            print(f"  Current document count: {count}")

            if count > 0:
                print("  Skipping knowledge base initialization")
                return

        # Load knowledge base documents
        print("Loading knowledge base documents...")

        if not KNOWLEDGE_BASE_DIR.exists():
            print(f"⚠ Knowledge base directory not found: {KNOWLEDGE_BASE_DIR}")
            print("  Creating empty directory...")
            os.makedirs(KNOWLEDGE_BASE_DIR, exist_ok=True)
            return

        # Count markdown files
        md_files = list(KNOWLEDGE_BASE_DIR.glob("*.md"))
        print(f"Found {len(md_files)} markdown documents")

        if len(md_files) == 0:
            print("⚠ No markdown files found in knowledge base directory")
            return

        # Initialize knowledge base
        initialize_knowledge_base()

        # Verify loaded documents
        collection = client.get_collection("acme_knowledge_base")
        count = collection.count()
        print(f"✓ Knowledge base initialized with {count} documents")

    except Exception as e:
        print(f"✗ Failed to initialize ChromaDB: {e}")
        raise


def main():
    """Main initialization routine"""
    print("=" * 60)
    print("AI Testing Resource - Database Initialization")
    print("=" * 60)

    try:
        # Initialize TSR database
        initialize_tsr_database()

        # Initialize ChromaDB
        initialize_chroma_database()

        print("\n" + "=" * 60)
        print("✓ Initialization complete!")
        print("=" * 60)
        return 0

    except Exception as e:
        print("\n" + "=" * 60)
        print(f"✗ Initialization failed: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
```

### 4. Test Data Seeding Script

**File:** `scripts/seed_test_data.py`

```python
#!/usr/bin/env python3
"""
Seed the TSR database with sample test data for development and testing
"""

import sys
import uuid
from pathlib import Path
from datetime import datetime, timedelta
import json

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tsr.models import (
    TestSummaryReport, VersionManifest, TestTypeResult, TestType,
    EvalIterationSummary, FailureMode, RequirementCoverage, GoNoGoDecision
)
from tsr.repository import TSRRepository
from tsr.rules import GoNoGoEvaluator
from config import TSR_DATABASE_URL


def create_sample_version_manifest(iteration: int) -> VersionManifest:
    """Create version manifest for iteration"""
    return VersionManifest(
        codebase_sha=f"abc123{iteration}" + "0" * 34,
        codebase_branch="main",
        codebase_repo="https://github.com/example/ai-testing-resource",
        testbase_sha=f"def456{iteration}" + "0" * 34,
        prompts_sha=f"ghi789{iteration}" + "0" * 34,
        prompts_version=f"v1.{iteration}.0"
    )


def create_sample_test_results(iteration: int) -> list:
    """Create sample test results with iteration-specific pass rates"""
    # V1: Some failures, V2: Better, V3: All pass
    failure_counts = {
        1: {'unit': 2, 'security': 1, 'evals': 5},
        2: {'unit': 0, 'security': 0, 'evals': 2},
        3: {'unit': 0, 'security': 0, 'evals': 0}
    }

    base_counts = {
        'unit': 45,
        'integration': 12,
        'e2e': 8,
        'acceptance': 6,
        'evals': 15,
        'security': 10,
        'performance': 5
    }

    results = []
    for test_type, total in base_counts.items():
        failed = failure_counts.get(iteration, {}).get(test_type, 0)
        passed = total - failed

        results.append(TestTypeResult(
            test_type=TestType(test_type),
            total=total,
            passed=passed,
            failed=failed,
            skipped=0,
            duration_ms=(total * 150) + (iteration * 100),
            failure_details=[]
        ))

    return results


def create_sample_eval_iterations(up_to_iteration: int) -> list:
    """Create eval iteration history"""
    iterations = []

    # V1: Verbose
    if up_to_iteration >= 1:
        iterations.append(EvalIterationSummary(
            iteration=1,
            version_name="V1 Verbose",
            prompt_version="v1.0",
            outcome="failed",
            metrics={
                "accuracy": 0.65,
                "avg_response_length": 320,
                "grounding_score": 0.0,
                "latency_p95": 2850
            },
            failure_modes=[
                FailureMode(
                    id=str(uuid.uuid4()),
                    name="Excessive verbosity",
                    description="Responses exceed 300 words vs 80-word target",
                    severity="major",
                    category="format",
                    discovered_in_iteration=1,
                    resolution_status="fixed"
                )
            ],
            fixes_applied=[]
        ))

    # V2: Concise but hallucinating
    if up_to_iteration >= 2:
        iterations.append(EvalIterationSummary(
            iteration=2,
            version_name="V2 No RAG",
            prompt_version="v2.0",
            outcome="improved",
            metrics={
                "accuracy": 0.75,
                "avg_response_length": 85,
                "grounding_score": 0.0,
                "latency_p95": 1250
            },
            failure_modes=[
                FailureMode(
                    id=str(uuid.uuid4()),
                    name="Hallucinated pricing",
                    description="Made up prices without access to real data",
                    severity="critical",
                    category="accuracy",
                    discovered_in_iteration=2,
                    resolution_status="fixed"
                )
            ],
            fixes_applied=[
                {"description": "Reduced max_tokens to 150", "iteration": 2}
            ]
        ))

    # V3: RAG-based, accurate
    if up_to_iteration >= 3:
        iterations.append(EvalIterationSummary(
            iteration=3,
            version_name="V3 RAG",
            prompt_version="v3.0",
            outcome="passed",
            metrics={
                "accuracy": 0.95,
                "avg_response_length": 82,
                "grounding_score": 0.92,
                "latency_p95": 1850
            },
            failure_modes=[],
            fixes_applied=[
                {"description": "Added ChromaDB RAG pipeline", "iteration": 3},
                {"description": "Added source citation requirement", "iteration": 3}
            ]
        ))

    return iterations


def create_sample_requirements() -> list:
    """Create sample requirement coverage"""
    return [
        RequirementCoverage(
            requirement_id="REQ-001",
            requirement_text="System must respond within 5 seconds (P95)",
            test_ids=["test_latency_p95", "test_performance_benchmark"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-002",
            requirement_text="Responses must cite source documents",
            test_ids=["test_grounding_citations", "eval_v3_grounding"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-003",
            requirement_text="No prompt injection vulnerabilities",
            test_ids=["test_prompt_injection", "test_security_validation"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-004",
            requirement_text="Response length ~80 words (±25%)",
            test_ids=["eval_v1_length", "test_format_word_count"],
            coverage_status="covered",
            verification_status="verified"
        ),
        RequirementCoverage(
            requirement_id="REQ-005",
            requirement_text="Factual accuracy ≥85%",
            test_ids=["eval_v2_accuracy", "eval_v3_grounding"],
            coverage_status="covered",
            verification_status="verified"
        )
    ]


def seed_tsr_data():
    """Seed database with sample TSR data"""
    print("\n=== Seeding TSR Test Data ===")

    try:
        engine = create_engine(TSR_DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        repository = TSRRepository(session)
        evaluator = GoNoGoEvaluator()

        # Check if data already exists
        existing_count = repository.count()
        if existing_count > 0:
            print(f"⚠ Database already contains {existing_count} TSRs")
            print("  Skipping seeding (delete TSRs manually if you want to reseed)")
            return

        print("Creating sample TSRs for three iterations...")

        # Create TSRs for each iteration
        for iteration in range(1, 4):
            print(f"\nCreating TSR for V{iteration}...")

            tsr = TestSummaryReport(
                id=str(uuid.uuid4()),
                created_at=datetime.utcnow() - timedelta(days=10 - iteration * 3),
                triggered_by="seeding_script",
                environment="test",
                versions=create_sample_version_manifest(iteration),
                test_results=create_sample_test_results(iteration),
                eval_iterations=create_sample_eval_iterations(iteration),
                requirement_coverage=create_sample_requirements()
            )

            # Apply go/no-go decision
            evaluator.apply_decision(tsr)

            # Save to database
            repository.save(tsr)

            print(f"  ✓ Created TSR {tsr.id[:8]} with decision: {tsr.go_no_go_decision.value}")
            print(f"    Total tests: {tsr.get_total_tests()}, Passed: {tsr.get_total_passed()}")
            print(f"    Eval iterations: {len(tsr.eval_iterations)}")
            print(f"    Blocking issues: {len(tsr.blocking_issues)}")

        # Print summary
        total_tsrs = repository.count()
        go_count = repository.count(decision='go')
        no_go_count = repository.count(decision='no_go')

        print("\n" + "=" * 60)
        print(f"✓ Seeding complete!")
        print(f"  Total TSRs: {total_tsrs}")
        print(f"  GO decisions: {go_count}")
        print(f"  NO-GO decisions: {no_go_count}")
        print("=" * 60)

    except Exception as e:
        print(f"✗ Failed to seed test data: {e}")
        import traceback
        traceback.print_exc()
        raise


if __name__ == '__main__':
    seed_tsr_data()
```

### 5. Monitoring Baseline Configuration

**File:** `scripts/init_monitoring_baselines.py`

```python
#!/usr/bin/env python3
"""
Initialize monitoring baselines from V3 traces (production-ready performance)
"""

import sys
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from monitoring.models import ProductionTrace, AnomalyThresholds
from monitoring.anomaly import AnomalyDetector
from monitoring.metrics import MetricsAggregator


def load_traces_from_file(trace_file: Path) -> list:
    """Load production traces from JSON file"""
    with open(trace_file, 'r') as f:
        data = json.load(f)

    traces = []
    for item in data:
        trace = ProductionTrace(
            id=item['id'],
            timestamp=datetime.fromisoformat(item['timestamp']),
            question=item['question'],
            response=item['response'],
            latency_ms=item['latency_ms'],
            prompt_tokens=item.get('prompt_tokens', 0),
            completion_tokens=item.get('completion_tokens', 0),
            model_version=item.get('model_version', 'unknown'),
            prompt_version=item.get('prompt_version', 'unknown'),
            sources=item.get('sources', []),
            user_feedback=item.get('user_feedback'),
            detected_category=item.get('detected_category'),
            anomaly_flags=item.get('anomaly_flags', [])
        )
        traces.append(trace)

    return traces


def calculate_baselines():
    """Calculate and save monitoring baselines"""
    print("\n=== Initializing Monitoring Baselines ===")

    # Load V3 traces (production-ready performance)
    v3_traces_file = Path(__file__).parent.parent / 'data' / 'traces' / 'v3_traces.json'

    if not v3_traces_file.exists():
        print(f"⚠ V3 traces file not found: {v3_traces_file}")
        print("  Creating default baselines from recommended values...")

        # Use recommended defaults from documentation
        baselines = {
            'latency_p95': 1850,
            'satisfaction_rate': 1.0,
            'source': 'default_recommendations',
            'timestamp': datetime.utcnow().isoformat()
        }

    else:
        print(f"Loading traces from: {v3_traces_file}")
        traces = load_traces_from_file(v3_traces_file)
        print(f"  Loaded {len(traces)} traces")

        # Calculate metrics using aggregator
        aggregator = MetricsAggregator()
        for trace in traces:
            aggregator.add_trace(trace)

        # Get metrics summary for entire period
        metrics = aggregator.get_summary(window_minutes=24 * 60)  # 24 hours

        baselines = {
            'latency_p50': metrics.latency_p50,
            'latency_p95': metrics.latency_p95,
            'latency_p99': metrics.latency_p99,
            'satisfaction_rate': metrics.satisfaction_rate,
            'avg_prompt_tokens': metrics.avg_prompt_tokens,
            'avg_completion_tokens': metrics.avg_completion_tokens,
            'trace_count': metrics.trace_count,
            'source': 'v3_traces',
            'timestamp': datetime.utcnow().isoformat()
        }

        print(f"\nCalculated baselines:")
        print(f"  P50 Latency: {baselines['latency_p50']:.0f}ms")
        print(f"  P95 Latency: {baselines['latency_p95']:.0f}ms")
        print(f"  P99 Latency: {baselines['latency_p99']:.0f}ms")
        print(f"  Satisfaction: {baselines['satisfaction_rate']:.1%}")
        print(f"  Avg Prompt Tokens: {baselines['avg_prompt_tokens']:.0f}")
        print(f"  Avg Completion Tokens: {baselines['avg_completion_tokens']:.0f}")

    # Save baselines to config file
    baselines_file = Path(__file__).parent.parent / 'config' / 'monitoring_baselines.json'
    baselines_file.parent.mkdir(exist_ok=True)

    with open(baselines_file, 'w') as f:
        json.dump(baselines, f, indent=2)

    print(f"\n✓ Baselines saved to: {baselines_file}")

    # Initialize detector with baselines
    detector = AnomalyDetector(thresholds=AnomalyThresholds(
        latency_p95_multiplier=1.5,
        error_rate_threshold=0.05,
        satisfaction_drop_threshold=0.10,
        grounding_score_min=0.85,
        window_minutes=15
    ))

    detector.set_baseline(
        latency_p95=baselines['latency_p95'],
        satisfaction=baselines['satisfaction_rate']
    )

    print("\n✓ Anomaly detector initialized with baselines")
    print(f"  Latency alert threshold: {baselines['latency_p95'] * 1.5:.0f}ms")
    print(f"  Satisfaction alert threshold: {baselines['satisfaction_rate'] - 0.10:.1%}")

    return baselines


if __name__ == '__main__':
    calculate_baselines()
```

**File:** `config/monitoring_baselines.json` (Generated by script)

```json
{
  "latency_p50": 1680,
  "latency_p95": 1850,
  "latency_p99": 1850,
  "satisfaction_rate": 1.0,
  "avg_prompt_tokens": 450,
  "avg_completion_tokens": 85,
  "trace_count": 3,
  "source": "v3_traces",
  "timestamp": "2024-01-31T12:00:00.000000"
}
```

### 6. Environment Configuration

**File:** `.env.docker` (Docker-specific environment)

```bash
# PostgreSQL (Docker Compose)
TSR_DATABASE_URL=postgresql://tsr_user:tsr_password@postgres:5432/tsr_db

# Flask
FLASK_DEBUG=False
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
SECRET_KEY=change-this-in-production-to-secure-random-key

# Anthropic AI (REQUIRED - set your API key)
ANTHROPIC_API_KEY=

# Model Configuration
ANTHROPIC_MODEL=claude-sonnet-4-20250514
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Paths (container paths)
CHROMA_PATH=/app/chroma_db

# Monitoring
MONITORING_ENABLED=True
MONITORING_WINDOW_MINUTES=15
TRACE_RETENTION_HOURS=24
SOCKETIO_MESSAGE_QUEUE=redis://redis:6379/0

# ChromaDB
ANONYMIZED_TELEMETRY=False

# Database initialization
FORCE_RECREATE_TABLES=no
```

### 7. Documentation Updates

**File:** `DOCKER_SETUP.md` (New documentation)

```markdown
# Docker Setup Guide

## Quick Start

### Prerequisites
- Docker 20.10+ and Docker Compose 2.0+
- Anthropic API key

### Local Development

1. **Set API Key**
   ```bash
   cp .env.docker .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

2. **Start Services**
   ```bash
   docker compose up -d
   ```

3. **Initialize Database (first time only)**
   ```bash
   docker compose exec api python scripts/init_database.py
   docker compose exec api python scripts/seed_test_data.py
   docker compose exec api python scripts/init_monitoring_baselines.py
   ```

4. **Access Application**
   - API: http://localhost:5000
   - Governance Portal: http://localhost:5000/governance/dashboard
   - Monitoring: http://localhost:5000/monitoring/traces

### CI/CD Testing

```bash
# Run tests in isolated environment
docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm api

# View test results
docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm api cat results/test-results.xml
```

## Commands

### Database Management

```bash
# Initialize fresh database
docker compose exec api python scripts/init_database.py

# Seed test data
docker compose exec api python scripts/seed_test_data.py

# Reset database (WARNING: deletes all data)
docker compose exec api python -c "
from sqlalchemy import create_engine
from tsr.database import drop_tables, create_tables
from config import TSR_DATABASE_URL
engine = create_engine(TSR_DATABASE_URL)
drop_tables(engine)
create_tables(engine)
"

# PostgreSQL shell
docker compose exec postgres psql -U tsr_user -d tsr_db
```

### Logs and Debugging

```bash
# View logs
docker compose logs -f api
docker compose logs -f postgres

# Shell access
docker compose exec api bash
docker compose exec postgres bash

# Run tests
docker compose exec api pytest tests/ -v
```

### Cleanup

```bash
# Stop services
docker compose down

# Remove volumes (WARNING: deletes all data)
docker compose down -v

# Full cleanup including images
docker compose down -v --rmi all
```

## Configuration

### Environment Variables

See `.env.docker` for all configuration options.

Key variables:
- `ANTHROPIC_API_KEY` - Required for AI functionality
- `TSR_DATABASE_URL` - PostgreSQL connection string
- `SOCKETIO_MESSAGE_QUEUE` - Redis for distributed WebSocket
- `MONITORING_ENABLED` - Enable/disable monitoring subsystem

### Volumes

- `postgres_data` - PostgreSQL database persistence
- `chroma_data` - ChromaDB vector store
- `./data` - Knowledge base and traces (bind mount)

### Ports

- `5000` - Flask API
- `5432` - PostgreSQL (exposed for local tools)
- `6379` - Redis (exposed for debugging)

## Production Deployment

For production deployment to AWS (deferred - will add Terraform later):
- Use managed PostgreSQL (RDS)
- Use managed Redis (ElastiCache)
- Deploy API to ECS/EKS
- Configure proper secrets management
- Enable SSL/TLS
- Set up monitoring and logging

## Troubleshooting

### Database Connection Failed
```bash
# Check PostgreSQL is healthy
docker compose ps postgres
docker compose logs postgres

# Verify connection string
docker compose exec api python -c "from config import TSR_DATABASE_URL; print(TSR_DATABASE_URL)"
```

### ChromaDB Initialization Failed
```bash
# Check permissions
docker compose exec api ls -la /app/chroma_db

# Verify knowledge base
docker compose exec api ls -la /app/data/knowledge_base
```

### API Won't Start
```bash
# Check environment variables
docker compose exec api env | grep -E 'ANTHROPIC|DATABASE|FLASK'

# Test database connection
docker compose exec api python -c "
from sqlalchemy import create_engine
from config import TSR_DATABASE_URL
engine = create_engine(TSR_DATABASE_URL)
with engine.connect() as conn:
    print('Connection successful')
"
```
```

### 8. CI/CD Integration Update

**File:** `.github/workflows/ai-app-ci.yml` (Update complete workflow)

**Changes:**
1. Update trigger to run on all branches: `branches: ["**"]`
2. Replace all `docker-compose` with `docker compose`
3. Ensure artifacts are uploaded for all test runs
4. Add proper cleanup

```yaml
name: AI Application CI/CD

on:
  push:
    branches: ["**"]  # Run on all branches (including feature branches)
  pull_request:
    branches: [main]  # Run on PRs to main

env:
  TSR_API_URL: ${{ secrets.TSR_API_URL || 'http://localhost:5000' }}

jobs:
  test-and-evaluate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0  # Full history for git operations

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Start Docker Compose services
        run: |
          cp .env.docker .env
          echo "ANTHROPIC_API_KEY=${{ secrets.ANTHROPIC_API_KEY }}" >> .env
          docker compose -f docker-compose.yml -f docker-compose.ci.yml up -d

      - name: Wait for services to be healthy
        run: |
          timeout 120 bash -c 'until docker compose ps | grep -q "healthy"; do sleep 5; done'

      - name: Run tests and generate TSR
        id: tsr
        run: |
          # Tests run automatically via docker-compose.ci.yml command
          docker compose exec -T api pytest tests/ --junitxml=results/test-results.xml -v

          # Generate TSR
          docker compose exec -T api python scripts/generate_tsr.py \
            --results-dir results/ \
            --codebase-sha ${{ github.sha }} \
            --environment ci \
            --triggered-by github-actions \
            --output tsr.json \
            --pretty

          # Copy TSR to host
          docker compose exec -T api cat tsr.json > tsr.json

          # Extract TSR ID for later steps
          TSR_ID=$(cat tsr.json | python -c "import sys, json; print(json.load(sys.stdin)['id'])")
          echo "tsr_id=$TSR_ID" >> $GITHUB_OUTPUT

      - name: Upload TSR to API
        if: always()
        run: |
          curl -X POST $TSR_API_URL/api/tsr \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer ${{ secrets.TSR_API_TOKEN }}" \
            -d @tsr.json \
            -f || echo "TSR upload failed (non-blocking)"

      - name: Check Go/No-Go Decision
        id: go_no_go
        run: |
          # Get decision from TSR
          DECISION=$(cat tsr.json | python -c "import sys, json; print(json.load(sys.stdin)['go_no_go_decision'])")
          echo "decision=$DECISION" >> $GITHUB_OUTPUT

          if [ "$DECISION" = "no_go" ]; then
            echo "::error::Deployment blocked: NO-GO decision"

            # Extract blocking issues
            cat tsr.json | python -c "
import sys, json
tsr = json.load(sys.stdin)
for issue in tsr.get('blocking_issues', []):
    print(f'::error::{issue}')
"
            exit 1
          elif [ "$DECISION" = "pending_review" ]; then
            echo "::warning::Manual approval required"
          else
            echo "::notice::GO decision - proceeding with deployment"
          fi

      - name: Upload TSR Artifact
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-summary-report
          path: |
            tsr.json
            results/*.xml

      - name: Cleanup
        if: always()
        run: docker compose down -v

  deploy-staging:
    needs: test-and-evaluate
    if: github.ref == 'refs/heads/main' && needs.test-and-evaluate.outputs.decision == 'go'
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Staging
        run: |
          echo "Deploying to staging..."
          # Add your deployment commands here
          # ./scripts/deploy-staging.sh

      - name: Run Smoke Tests
        run: |
          echo "Running staging smoke tests..."
          # pytest tests/smoke --env=staging

      - name: Notify Success
        if: success()
        run: |
          echo "✅ Deployment to staging successful!"

  deploy-production:
    needs: deploy-staging
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://your-app.com

    steps:
      - uses: actions/checkout@v4

      - name: Deploy to Production
        run: |
          echo "Deploying to production..."
          # Add your deployment commands here
          # ./scripts/deploy-production.sh

      - name: Notify Success
        if: success()
        run: |
          echo "🚀 Production deployment successful!"
```

## Critical Files

### Files to Update (Docker Compose V2 Syntax)

All files have already been created but need to be updated with `docker compose` syntax:

1. **DOCKER_SETUP.md** - Update all `docker-compose` to `docker compose`
2. **IMPLEMENTATION_SUMMARY.md** - Update all `docker-compose` to `docker compose`
3. **DOCKER_IMPLEMENTATION_CHECKLIST.md** - Update all `docker-compose` to `docker compose`
4. **README.md** - Update Docker commands to use `docker compose`
5. **.github/workflows/ai-app-ci.yml** - Update workflow triggers and commands:
   - Change `branches: [main, staging]` to `branches: ["**"]`
   - Replace all `docker-compose` with `docker compose`

### Already Created Files (No Changes Needed)
- `docker-compose.yml` - Main orchestration (file syntax is correct)
- `docker-compose.ci.yml` - CI/CD override (file syntax is correct)
- `Dockerfile` - API container image
- `.dockerignore` - Build optimization
- `scripts/init_database.py` - Database initialization
- `scripts/seed_test_data.py` - Test data seeding
- `scripts/init_monitoring_baselines.py` - Monitoring baseline setup
- `.env.docker` - Docker environment template
- `config/monitoring_baselines.json` - Generated baseline config
- All Python code in `app/`, `tsr/`, `monitoring/`, `viewer/`
- All test files in `tests/`
- `requirements.txt`
- `config.py`

## Verification Steps

After implementation, verify the setup:

### 1. Local Development
```bash
# Start services
docker compose up -d

# Check health
docker compose ps
curl http://localhost:5000/api/tsr/stats

# Access web interface
open http://localhost:5000/governance/dashboard
open http://localhost:5000/monitoring/traces
```

### 2. Database Verification
```bash
# Check TSR tables
docker compose exec postgres psql -U tsr_user -d tsr_db -c "\dt"

# Check seeded data
docker compose exec api python -c "
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
docker compose exec api python -c "
from app.rag import get_collection
collection = get_collection()
print(f'Documents in knowledge base: {collection.count()}')
"
```

### 4. Monitoring Verification
```bash
# Check baseline configuration
docker compose exec api cat config/monitoring_baselines.json

# Test anomaly detector
docker compose exec api python -c "
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

### 5. Local Testing with Artifact Generation
```bash
# Run full test suite and generate artifacts locally
mkdir -p results

# Start services
docker compose up -d

# Wait for services to be healthy
sleep 10

# Run tests with XML output
docker compose exec api pytest tests/ --junitxml=results/test-results.xml -v

# Generate TSR artifact
docker compose exec api python scripts/generate_tsr.py \
  --results-dir results/ \
  --codebase-sha $(git rev-parse HEAD) \
  --environment local \
  --triggered-by local-testing \
  --output tsr.json \
  --pretty

# Copy artifacts from container to host
docker compose cp api:/app/results/test-results.xml ./results/
docker compose cp api:/app/tsr.json ./tsr.json

# Verify artifacts
echo "=== Test Results Summary ==="
grep -E "tests=\"|errors=\"|failures=\"" results/test-results.xml

echo "=== TSR Summary ==="
cat tsr.json | python -c "
import sys, json
tsr = json.load(sys.stdin)
print(f'TSR ID: {tsr[\"id\"]}')
print(f'Decision: {tsr[\"go_no_go_decision\"]}')
print(f'Total Tests: {sum(r[\"total\"] for r in tsr[\"test_results\"])}')
print(f'Passed: {sum(r[\"passed\"] for r in tsr[\"test_results\"])}')
print(f'Failed: {sum(r[\"failed\"] for r in tsr[\"test_results\"])}')
print(f'Blocking Issues: {len(tsr[\"blocking_issues\"])}')
"

# Cleanup
docker compose down -v
```

### 6. CI/CD Test (Full Simulation)
```bash
# Run complete CI workflow locally
docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm api

# Should:
# - Initialize database
# - Seed test data
# - Run all tests
# - Generate TSR
# - Exit with code 0 if all pass
```

## Local Testing Procedure

Before pushing to GitHub, run the complete test suite locally:

```bash
#!/bin/bash
# test-local.sh - Comprehensive local testing script

set -e  # Exit on error

echo "=== AI Testing Resource - Local Validation ==="
echo ""

# 1. Setup environment
echo "1. Setting up environment..."
cp .env.docker .env
# Add your ANTHROPIC_API_KEY to .env manually or via:
# echo "ANTHROPIC_API_KEY=your-key-here" >> .env

# 2. Start services
echo "2. Starting Docker Compose services..."
docker compose up -d

# 3. Wait for health checks
echo "3. Waiting for services to be healthy..."
sleep 15
docker compose ps

# 4. Run test suite
echo "4. Running test suite..."
mkdir -p results
docker compose exec -T api pytest tests/ \
  --junitxml=results/test-results.xml \
  -v \
  --tb=short

# 5. Generate TSR
echo "5. Generating Test Summary Report..."
docker compose exec -T api python scripts/generate_tsr.py \
  --results-dir results/ \
  --codebase-sha "$(git rev-parse HEAD)" \
  --environment local \
  --triggered-by local-testing \
  --output tsr.json \
  --pretty

# 6. Copy artifacts
echo "6. Copying artifacts from container..."
docker compose cp api:/app/results/test-results.xml ./results/
docker compose cp api:/app/tsr.json ./tsr.json

# 7. Display results
echo ""
echo "=== Test Results Summary ==="
python3 << 'EOF'
import xml.etree.ElementTree as ET
tree = ET.parse('results/test-results.xml')
root = tree.getroot()
testsuite = root.find('.//testsuite')
print(f"Tests: {testsuite.get('tests')}")
print(f"Errors: {testsuite.get('errors')}")
print(f"Failures: {testsuite.get('failures')}")
print(f"Skipped: {testsuite.get('skipped')}")
print(f"Time: {testsuite.get('time')}s")
EOF

echo ""
echo "=== TSR Summary ==="
python3 << 'EOF'
import json
with open('tsr.json') as f:
    tsr = json.load(f)
print(f"TSR ID: {tsr['id']}")
print(f"Decision: {tsr['go_no_go_decision']}")
print(f"Total Tests: {sum(r['total'] for r in tsr['test_results'])}")
print(f"Passed: {sum(r['passed'] for r in tsr['test_results'])}")
print(f"Failed: {sum(r['failed'] for r in tsr['test_results'])}")
print(f"Blocking Issues: {len(tsr['blocking_issues'])}")
if tsr['blocking_issues']:
    print("\nBlocking Issues:")
    for issue in tsr['blocking_issues']:
        print(f"  - {issue}")
EOF

# 8. Verify artifacts
echo ""
echo "=== Artifacts Generated ==="
ls -lh results/test-results.xml tsr.json

# 9. Cleanup
echo ""
echo "9. Cleaning up..."
docker compose down -v

echo ""
echo "=== Validation Complete ==="
echo "Artifacts available in:"
echo "  - ./results/test-results.xml"
echo "  - ./tsr.json"
echo ""
echo "Ready to push to GitHub!"
```

Save this as `test-local.sh`, make it executable, and run:

```bash
chmod +x test-local.sh
./test-local.sh
```

## Success Criteria

### Local Testing
✅ Docker Compose V2 syntax used everywhere (`docker compose`)
✅ Services start successfully with health checks
✅ Database tables created automatically on first run
✅ Knowledge base initialized with documents
✅ Test data seeded successfully
✅ Monitoring baselines configured
✅ All tests pass locally
✅ TSR generated with artifacts
✅ Artifacts can be extracted from container
✅ Go/No-Go decision is "go"
✅ Volumes persist data across restarts

### CI/CD Integration
✅ GitHub Actions runs on all branches (feature branches)
✅ GitHub Actions runs on PRs to main
✅ All `docker-compose` commands replaced with `docker compose`
✅ Tests pass in GitHub Actions
✅ TSR artifact uploaded to GitHub
✅ Can download and review artifacts via `gh run download`
✅ Can use Claude to check PR status via `gh pr checks`
✅ Can use Claude to view logs via `gh run view --log`

### Documentation
✅ DOCKER_SETUP.md updated with `docker compose` commands
✅ IMPLEMENTATION_SUMMARY.md updated
✅ DOCKER_IMPLEMENTATION_CHECKLIST.md updated
✅ README.md updated with Docker quick start
✅ GitHub PR integration documented
✅ Claude monitoring workflow documented

## GitHub PR Integration with Claude

### Overview
Claude can monitor GitHub Actions status and help debug failed CI runs by accessing PR information through the GitHub API.

### Setup

1. **Install GitHub CLI** (if not already installed)
   ```bash
   brew install gh  # macOS
   # or download from https://cli.github.com/
   ```

2. **Authenticate GitHub CLI**
   ```bash
   gh auth login
   # Follow prompts to authenticate
   ```

3. **Verify Authentication**
   ```bash
   gh auth status
   ```

### Monitoring PR Status

When you push to a feature branch and create a PR, use Claude to check the status:

#### Check PR Status
```bash
# List open PRs
gh pr list

# View specific PR details
gh pr view <PR_NUMBER>

# Check PR status including GitHub Actions
gh pr checks <PR_NUMBER>
```

#### View GitHub Actions Logs
```bash
# List workflow runs for current branch
gh run list --branch <BRANCH_NAME>

# View specific run details
gh run view <RUN_ID>

# Download workflow run logs
gh run download <RUN_ID>

# View logs in terminal
gh run view <RUN_ID> --log
```

### Claude + GitHub Workflow

1. **Push feature branch and create PR**
   ```bash
   git checkout -b feature/add-docker-compose
   git add .
   git commit -m "Add Docker Compose setup"
   git push -u origin feature/add-docker-compose

   # Create PR
   gh pr create --title "Add Docker Compose setup" \
     --body "Implements Docker Compose for local development and CI"
   ```

2. **Ask Claude to monitor the PR**
   - "Can you check the status of PR #123?"
   - Claude will run: `gh pr checks 123`

3. **If tests fail, ask Claude to investigate**
   - "The tests failed on PR #123, can you check the logs?"
   - Claude will run: `gh run view <RUN_ID> --log`
   - Claude can then analyze the error and suggest fixes

4. **After fixing issues, push updates**
   ```bash
   git add .
   git commit -m "Fix test failures"
   git push
   ```
   - GitHub Actions will automatically re-run tests
   - Ask Claude to check status again

### Example Claude Commands

```
# After creating a PR
User: "I just created PR #15 for the Docker Compose setup. Can you check if the tests passed?"

Claude: [Runs gh pr checks 15 and reports status]

# If tests failed
User: "The tests failed. Can you look at the logs and tell me what went wrong?"

Claude: [Runs gh run view --log and analyzes the error]

# After pushing fix
User: "I pushed a fix. Can you verify the tests are passing now?"

Claude: [Checks latest run status]
```

### GitHub Actions Workflow (Feature Branch Testing)

The workflow is configured to run on **all branches** when code is pushed:

```yaml
on:
  push:
    branches: ["**"]  # Run on all branches
  pull_request:
    branches: [main]  # Run on PRs to main
```

This means:
- **Feature branches**: Tests run automatically on every push
- **Pull requests**: Tests run when PR is opened or updated
- **Main branch**: Tests run before deployment

### Best Practices

1. **Create feature branches for all changes**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Push early and often**
   - GitHub Actions will test each push
   - Catch issues early before merging to main

3. **Review test results before merging**
   - Use `gh pr checks` to verify all tests pass
   - Review TSR artifact for go/no-go decision

4. **Use Claude for debugging**
   - Claude can access GitHub Actions logs
   - Ask Claude to explain test failures
   - Claude can suggest fixes based on error messages

### Artifact Access

GitHub Actions uploads test artifacts that you can download:

```bash
# List artifacts for a run
gh run view <RUN_ID> --log

# Download artifacts
gh run download <RUN_ID>

# View TSR JSON
cat test-summary-report/tsr.json | jq .

# View test results
cat test-summary-report/test-results.xml
```

## Notes

- **Docker Compose V2**: Use `docker compose` (not `docker-compose`)
- **PostgreSQL** chosen over SQLite for multi-container support
- **Redis** optional but enables distributed WebSocket (production-ready)
- **Health checks** ensure proper startup ordering
- **Volume mounts** separate code (bind) from data (volumes)
- **CI override** uses tmpfs for faster tests
- **Baseline calculation** uses V3 traces (production-ready performance)
- **Seeding** creates 3 sample TSRs matching V1/V2/V3 evolution
- **Feature branch testing** ensures code quality before merging to main
- **GitHub CLI integration** enables Claude to monitor and debug CI runs
- **Production deployment** deferred - will add Terraform for AWS later
