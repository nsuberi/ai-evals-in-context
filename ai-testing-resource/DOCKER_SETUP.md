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
