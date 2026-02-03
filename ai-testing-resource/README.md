# AI Testing Resource

An interactive Flask application that teaches how AI evaluations fit into the classical testing pyramid.

## Core Thesis

**AI Evals are acceptance tests for AI behavior.** They verify the AI does what you want it to do, while traditional tests handle the deterministic aspects of the software.

## Features

- **Sample App**: Acme Widgets support bot with three iterative versions (V1: Verbose, V2: Hallucinating, V3: Accurate)
- **Test Suite**: Unit, integration, e2e, acceptance, security, performance, and AI eval tests
- **Educational Viewer**: Browse tests, inspect traces, and understand the iteration process
- **Governance Portal**: TSR dashboard with go/no-go rules engine and approval workflows
- **Production Monitoring**: Real-time trace streaming with anomaly and drift detection

## Quick Start: Local Python

```bash
# 1. Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 4. Initialize knowledge base
python -c "from app.rag import initialize_knowledge_base; initialize_knowledge_base()"

# 5. Run the application
python run.py
```

Open in browser: `http://localhost:5000`

## Quick Start: Docker Compose

```bash
# 1. Set API key
cp .env.docker .env
# Edit .env and add your ANTHROPIC_API_KEY

# 2. Start services
docker compose up -d

# 3. Access application
open http://localhost:5001
```

## Browser Routes

| Route | Description |
|-------|-------------|
| `/` | Redirects to ask page |
| `/ask` | Demo support bot |
| `/viewer/tests` | Test Navigator |
| `/viewer/traces` | Trace Inspector |
| `/viewer/timeline` | Iteration Timeline |
| `/governance/dashboard` | TSR Dashboard |
| `/monitoring/traces` | Live Monitoring |

## The Three Versions

| Version | Issue | Result |
|---------|-------|--------|
| **V1 - Verbose** | System prompt asks for 300+ word responses | Fails length evals (users want ~80 words) |
| **V2 - Hallucinating** | No access to actual company data | Confidently makes up pricing and policies |
| **V3 - Accurate (RAG)** | Uses Chroma for retrieval-augmented generation | Concise AND accurate responses |

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests
pytest

# Run specific test type
pytest tests/unit/
pytest tests/evals/

# Run with coverage
pytest --cov=app --cov=viewer
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key | Required |
| `ANTHROPIC_MODEL` | Claude model to use | claude-sonnet-4-20250514 |
| `FLASK_DEBUG` | Enable debug mode | True |
| `FLASK_PORT` | Port to run on | 5000 |
| `CHROMA_PATH` | Path to Chroma database | ./chroma_db |
| `TSR_DATABASE_URL` | PostgreSQL connection (Docker) | postgresql://... |
| `MONITORING_ENABLED` | Enable monitoring subsystem | True |

## Project Structure

```
ai-testing-resource/
├── app/                    # Sample App: Acme Support Bot
│   ├── ai_service.py       # V1, V2, V3 implementations
│   ├── rag.py              # Chroma RAG pipeline
│   └── utils.py            # Input sanitization, token counting
│
├── viewer/                 # Educational Viewer
│   ├── routes.py           # Flask routes
│   ├── governance.py       # TSR dashboard routes
│   └── templates/          # Jinja2 templates
│
├── tsr/                    # Test Summary Report subsystem
│   ├── models.py           # Data models
│   ├── rules.py            # Go/no-go engine
│   ├── generator.py        # TSR generation
│   └── api.py              # REST API
│
├── monitoring/             # Production monitoring
│   ├── anomaly.py          # Anomaly detection
│   ├── drift.py            # Drift detection
│   └── stream.py           # WebSocket streaming
│
├── tests/                  # Complete Test Suite
│   ├── unit/               # Deterministic function tests
│   ├── integration/        # Component interaction tests
│   ├── e2e/                # Full user flow tests
│   ├── acceptance/         # Requirement verification
│   ├── evals/              # AI behavior evaluations
│   ├── security/           # Prompt injection tests
│   └── performance/        # Latency and token tests
│
├── data/
│   ├── knowledge_base/     # RAG documents
│   ├── traces/             # Pre-generated AI traces
│   └── explanations/       # Educational content
│
└── scripts/                # Utility scripts
    ├── init_database.py    # Database initialization
    ├── seed_test_data.py   # Sample data seeding
    └── generate_tsr.py     # TSR generation CLI
```

## Docker Commands Reference

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f api

# Run tests in container
docker compose exec api pytest tests/ -v

# Database shell
docker compose exec postgres psql -U tsr_user -d tsr_db

# Stop services
docker compose down

# Full reset (deletes all data)
docker compose down -v
```
