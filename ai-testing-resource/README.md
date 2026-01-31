# AI Testing Resource

An interactive Flask application that teaches how AI evaluations fit into the classical testing pyramid.

## Core Thesis

**AI Evals are acceptance tests for AI behavior.** They verify the AI does what you want it to do, while traditional tests handle the deterministic aspects of the software.

## Features

- **Sample App**: Acme Widgets support bot with three iterative versions (V1: Verbose, V2: Hallucinating, V3: Accurate)
- **Test Suite**: Complete test suite demonstrating unit, integration, e2e, acceptance, security, performance, and AI eval tests
- **Educational Viewer**: Browse tests, inspect traces, and understand the iteration process

## Quick Start

### Option 1: Docker (Recommended)

The easiest way to get started with a complete environment including PostgreSQL and Redis:

1. **Set up environment**
   ```bash
   cp .env.docker .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

2. **Start services**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - API: http://localhost:5000
   - Governance Portal: http://localhost:5000/governance/dashboard
   - Monitoring: http://localhost:5000/monitoring/traces
   - Test Navigator: http://localhost:5000/viewer/tests

See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker instructions.

### Option 2: Local Python Development

1. **Create and activate a virtual environment**
   ```bash
   # Create virtual environment
   python -m venv .venv

   # Activate virtual environment
   # On macOS/Linux:
   source .venv/bin/activate

   # On Windows:
   .venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

4. **Initialize the knowledge base**
   ```bash
   python -c "from app.rag import initialize_knowledge_base; initialize_knowledge_base()"
   ```

5. **Run the application**
   ```bash
   python run.py
   ```

6. **Open in browser**
   - Test Navigator: http://localhost:5000/viewer/tests
   - Trace Inspector: http://localhost:5000/viewer/traces
   - Demo: http://localhost:5000/ask

## Project Structure

```
ai-testing-resource/
├── app/                    # Sample App: Acme Support Bot
│   ├── ai_service.py      # V1, V2, V3 implementations
│   ├── rag.py             # Chroma RAG pipeline
│   └── utils.py           # Input sanitization, token counting
│
├── viewer/                 # Educational Viewer
│   ├── routes.py          # Flask routes
│   ├── test_navigator.py  # Test browsing logic
│   └── trace_inspector.py # Trace viewing logic
│
├── tests/                  # Complete Test Suite
│   ├── unit/              # Deterministic function tests
│   ├── integration/       # Component interaction tests
│   ├── e2e/               # Full user flow tests
│   ├── acceptance/        # Requirement verification
│   ├── evals/             # AI behavior evaluations
│   ├── security/          # Prompt injection tests
│   └── performance/       # Latency and token tests
│
├── data/
│   ├── knowledge_base/    # RAG documents
│   ├── traces/            # Pre-generated AI traces
│   └── explanations/      # Educational content
│
└── static/                # CSS and JavaScript
```

## The Three Versions

### V1 - Verbose
The system prompt asks for 300+ word responses. This fails length evals because users want concise ~80 word answers.

### V2 - Hallucinating
Fixed the length issue, but the model has no access to actual company data. It confidently makes up pricing and policy details.

### V3 - Accurate (RAG)
Uses retrieval-augmented generation with Chroma to fetch actual company documents. Responses are both concise AND accurate.

## Running Tests

Make sure your virtual environment is activated before running tests:

```bash
# Activate virtual environment if not already active
source .venv/bin/activate  # macOS/Linux
# or .venv\Scripts\activate  # Windows

# Run all tests
pytest

# Run specific test type
pytest tests/unit/
pytest tests/evals/

# Run with coverage
pytest --cov=app --cov=viewer
```

## AI Evals

The evals demonstrate how to test AI behavior:

- **eval_v1_length.py**: Tests that responses are ~80 words (V1 fails)
- **eval_v2_accuracy.py**: Tests factual accuracy (V2 fails)
- **eval_v3_grounding.py**: Tests that responses cite sources (V3 passes)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| ANTHROPIC_API_KEY | Your Anthropic API key | Required |
| ANTHROPIC_MODEL | Claude model to use | claude-sonnet-4-20250514 |
| FLASK_DEBUG | Enable debug mode | True |
| FLASK_PORT | Port to run on | 5000 |
| CHROMA_PATH | Path to Chroma database | ./chroma_db |
| EMBEDDING_MODEL | Sentence-transformers model | all-MiniLM-L6-v2 |
| ANONYMIZED_TELEMETRY | Disable ChromaDB telemetry | True |

## Telemetry

### ChromaDB Telemetry Errors (Non-Fatal)

When running the application, you may see these error messages during startup:
```
Failed to send telemetry event ClientStartEvent: capture() takes 1 positional argument but 3 were given
Failed to send telemetry event ClientCreateCollectionEvent: capture() takes 1 positional argument but 3 were given
```

**These errors are benign and do not affect functionality.** They occur due to a version/API mismatch in ChromaDB 0.5.23's internal telemetry system. The application will continue to work normally.

### What is ChromaDB Telemetry?

ChromaDB collects **anonymized product telemetry** to understand usage patterns and prioritize features and bug fixes. This is separate from this application's trace collection system (which tracks AI responses and evaluations).

For more details, see [ChromaDB's telemetry documentation](https://docs.trychroma.com/docs/overview/telemetry).

### Disabling Telemetry (Optional)

If you prefer to disable ChromaDB's telemetry, you have two options:

#### Option 1: Environment Variable
Add to your `.env` file:
```bash
ANONYMIZED_TELEMETRY=False
```

#### Option 2: Client Settings
Modify `app/rag.py` in the `get_chroma_client()` function:
```python
from chromadb.config import Settings

def get_chroma_client():
    global _chroma_client
    if _chroma_client is None:
        _chroma_client = chromadb.PersistentClient(
            path=CHROMA_PATH,
            settings=Settings(anonymized_telemetry=False)
        )
    return _chroma_client
```

## Dependencies

This project uses specific version constraints to ensure compatibility:

- **NumPy < 2.0**: ChromaDB 0.5.x requires NumPy 1.x due to its dependency on onnxruntime, which hasn't yet added full NumPy 2.0 support. The version constraint `numpy>=1.22.5,<2.0.0` prevents the `AttributeError: np.float_` error.

- **ChromaDB 0.5.23**: Upgraded from 0.4.x for better stability and bug fixes while maintaining API compatibility with the RAG implementation.

All dependencies are managed in `requirements.txt` and should be installed in a virtual environment to avoid conflicts with other projects.

## Design Philosophy

**Tests are the star of the show.** The viewer uses a dark chrome with light code canvases to create visual hierarchy where test code commands attention. Educational content supports but never competes with the code.

---

# Phase 2: Production Features

Phase 2 extends the AI Testing Resource with production-grade features for enterprise deployment:

## New Features

### 1. Enhanced Code Viewer
- **Line Numbers & Selection**: Click or shift-click to select lines
- **Keyboard Navigation**: Vim-style navigation (j/k/y/g/Escape)
- **Shareable Links**: Copy URLs with line selections
- **Copy to Clipboard**: Yank selected code sections

### 2. Test Summary Report (TSR)
- **Version Tracking**: Git SHAs for code, tests, and prompts
- **Test Results**: Aggregated results by test type
- **Eval History**: Iteration timeline (V1→V2→V3) with metrics
- **Go/No-Go Decision**: Automated deployment gates
- **Failure Modes**: Tracked issues with resolution status
- **Requirement Coverage**: Traceability matrix

### 3. CI/CD Integration
- **Automated TSR Generation**: From JUnit XML test results
- **REST API**: Query and approve TSRs programmatically
- **Pipeline Gates**: Block deployments on NO-GO decisions
- **Manual Approval**: For pending review cases

### 4. Governance Portal
- **TSR Dashboard**: Browse and filter all test reports
- **Detailed View**: Complete TSR with all sections
- **Compliance Checklist**: Auto-evaluated against rules
- **Approval Workflow**: Track who approved and when

### 5. Production Monitoring
- **Live Trace Feed**: Real-time AI interactions via WebSocket
- **Anomaly Detection**: Latency, error rate, satisfaction monitoring
- **Drift Detection**: Compare production to eval baseline
- **Metrics Dashboard**: P50/P95/P99 latency, error rates, satisfaction

## Quick Start (Phase 2)

### Database Setup

For development, Phase 2 uses SQLite by default. For production, use PostgreSQL:

```bash
# SQLite (default - no setup needed)
export TSR_DATABASE_URL="sqlite:///tsr.db"

# PostgreSQL (production)
export TSR_DATABASE_URL="postgresql://user:pass@localhost/tsr_db"
```

### Initialize TSR Database

```bash
python -c "from tsr.database import create_tables; from sqlalchemy import create_engine; from config import TSR_DATABASE_URL; create_tables(create_engine(TSR_DATABASE_URL))"
```

### Run with Monitoring Enabled

```bash
python run.py
```

Then access:
- **Governance Portal**: http://localhost:5000/governance/dashboard
- **Production Monitoring**: http://localhost:5000/monitoring/traces
- **TSR API**: http://localhost:5000/api/tsr

## Generating Test Summary Reports

### From CI/CD Pipeline

```bash
# Run tests
pytest tests/unit --junitxml=results/unit.xml
pytest tests/integration --junitxml=results/integration.xml
pytest tests/evals --junitxml=results/evals.xml

# Generate TSR
python scripts/generate_tsr.py \
  --results-dir results/ \
  --codebase-sha $(git rev-parse HEAD) \
  --environment test \
  --triggered-by ci \
  --output tsr.json \
  --exit-on-no-go
```

### Using the API

```bash
# Create TSR
curl -X POST http://localhost:5000/api/tsr \
  -H "Content-Type: application/json" \
  -d @tsr.json

# Get go/no-go decision
curl http://localhost:5000/api/tsr/{tsr_id}/go-no-go

# Approve TSR
curl -X POST http://localhost:5000/api/tsr/{tsr_id}/approve \
  -H "Content-Type: application/json" \
  -d '{"approved_by": "jane@example.com"}'
```

## CI/CD Pipeline Example

See `.github/workflows/ai-app-ci.yml` for a complete GitHub Actions workflow that:

1. Runs all test suites (unit, integration, e2e, security, evals)
2. Generates TSR from test results
3. Uploads TSR to API
4. Checks go/no-go decision
5. Blocks deployment on NO-GO
6. Deploys to staging on GO
7. Deploys to production after staging smoke tests

## Phase 2 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| TSR_DATABASE_URL | Database connection string | sqlite:///tsr.db |
| MONITORING_ENABLED | Enable production monitoring | True |
| MONITORING_WINDOW_MINUTES | Metrics aggregation window | 15 |
| TRACE_RETENTION_HOURS | How long to keep traces | 24 |
| SOCKETIO_MESSAGE_QUEUE | Redis URL for distributed WebSocket | None |

## Phase 2 Architecture

### TSR Subsystem
- **models.py**: Data classes for TSR, version manifest, test results
- **rules.py**: Go/no-go evaluation engine with configurable rules
- **generator.py**: Parse JUnit XML and generate TSRs
- **database.py**: SQLAlchemy models for persistence
- **repository.py**: Database operations layer
- **api.py**: REST API endpoints

### Monitoring Subsystem
- **models.py**: Production trace and metrics models
- **anomaly.py**: Anomaly detection with configurable thresholds
- **drift.py**: Compare production to eval baselines
- **metrics.py**: Aggregation of traces into summaries
- **stream.py**: WebSocket streaming for real-time updates

### Governance Portal
- **dashboard.html**: TSR list with filtering
- **tsr_detail.html**: Comprehensive TSR view
- **governance.py**: Flask routes for portal

## Go/No-Go Rules

Default rules can be customized in `tsr/rules.py`:

### Blocking Conditions
- All security tests must pass
- All unit tests must pass
- Eval accuracy ≥ 85%
- No unresolved critical failure modes
- Requirement coverage ≥ 95%

### Warning Conditions
- Grounding score ≥ 90%
- Performance test failure rate < 5%

## Monitoring Thresholds

Configure anomaly detection in monitoring:

```python
from monitoring import AnomalyThresholds

thresholds = AnomalyThresholds(
    latency_p95_multiplier=1.5,  # Alert if P95 > 1.5x baseline
    error_rate_threshold=0.05,    # Alert if error rate > 5%
    satisfaction_drop_threshold=0.10,  # Alert if satisfaction drops 10%
    grounding_score_min=0.85,     # Alert if grounding < 85%
    window_minutes=15             # Aggregation window
)
```

## Production Deployment

### Prerequisites
1. PostgreSQL database for TSR storage
2. Redis (optional) for distributed WebSocket support
3. Reverse proxy (nginx) for production serving
4. Process manager (systemd, supervisor) for reliability

### Example Production Setup

```bash
# Install dependencies
pip install -r requirements.txt gunicorn gevent

# Set environment
export TSR_DATABASE_URL="postgresql://user:pass@db.example.com/tsr"
export SOCKETIO_MESSAGE_QUEUE="redis://redis.example.com:6379/0"
export FLASK_DEBUG="False"
export SECRET_KEY="your-secure-secret-key"

# Initialize database
python -c "from tsr.database import create_tables; from sqlalchemy import create_engine; from config import TSR_DATABASE_URL; create_tables(create_engine(TSR_DATABASE_URL))"

# Run with gunicorn
gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
  -w 4 \
  -b 0.0.0.0:5000 \
  run:app
```

## Contributing

Contributions are welcome! Phase 2 focuses on production readiness:

- TSR generation and storage
- Go/no-go automation
- Real-time monitoring
- Governance and compliance features

## License

MIT License - See LICENSE file for details
