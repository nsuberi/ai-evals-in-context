# Docker Compose Testing Guide

This guide provides step-by-step instructions for testing the Docker Compose setup for the AI Testing Resource application.

## Prerequisites

1. **Start Docker Desktop** - Ensure Docker daemon is running
2. **Verify Docker Compose** is available:
   ```bash
   docker compose version
   ```
   Should show Docker Compose V2.x

## Testing Steps

### 1. Navigate to Project Directory

```bash
cd /Users/nathansuberi/Documents/GitHub/ai-evals-in-context/ai-testing-resource
```

### 2. Start Docker Compose Services

```bash
# Start all services in detached mode
docker compose up -d
```

Expected output:
- Creating network "tsr-network"
- Creating volumes "postgres_data" and "chroma_data"
- Starting containers: tsr-postgres, tsr-redis, tsr-api

### 3. Check Service Health

```bash
# Check all services are running and healthy
docker compose ps
```

All services should show status as `Up` or `Up (healthy)`.

### 4. Verify API Accessibility

```bash
# Test TSR stats endpoint
curl http://localhost:5000/api/tsr/stats

# Expected response: JSON with TSR statistics
```

### 5. Verify Database Tables

```bash
# Check PostgreSQL tables were created
docker compose exec postgres psql -U tsr_user -d tsr_db -c "\dt"
```

Expected tables:
- test_summary_reports
- test_results
- eval_iterations
- requirements
- go_no_go_decisions

### 6. Verify Test Data Seeding

```bash
# Check TSR count in database
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
print(f'GO decisions: {repo.count(decision=\"go\")}')
print(f'NO-GO decisions: {repo.count(decision=\"no_go\")}')
"
```

Expected: Should show at least 3 sample TSRs seeded.

### 7. Verify ChromaDB Knowledge Base

```bash
# Check ChromaDB collection
docker compose exec api python -c "
from app.rag import get_collection
collection = get_collection()
print(f'Documents in knowledge base: {collection.count()}')
"
```

Expected: Should show documents loaded from data/knowledge_base.

### 8. Verify Monitoring Baselines

```bash
# Check monitoring baseline configuration
docker compose exec api cat config/monitoring_baselines.json
```

Expected: JSON file with baseline metrics for latency and satisfaction.

### 9. Access Web Interfaces

Open in browser:

- **Governance Dashboard**: http://localhost:5000/governance/dashboard
- **Monitoring Traces**: http://localhost:5000/monitoring/traces
- **TSR Viewer**: http://localhost:5000/tsr/<tsr-id>

### 10. View Container Logs

```bash
# View all logs
docker compose logs

# View specific service logs
docker compose logs api
docker compose logs postgres
docker compose logs redis

# Follow logs in real-time
docker compose logs -f api
```

### 11. Test CI/CD Configuration

```bash
# Test CI workflow locally
docker compose -f docker-compose.yml -f docker-compose.ci.yml run --rm api
```

Expected:
- Database initialization
- Test data seeding
- All tests running
- Exit code 0 if tests pass

### 12. Cleanup

```bash
# Stop services but keep volumes
docker compose down

# Stop services and remove volumes (fresh start)
docker compose down -v
```

## Troubleshooting

### Services fail to start

Check logs:
```bash
docker compose logs postgres
docker compose logs redis
docker compose logs api
```

### Database connection errors

Ensure PostgreSQL is healthy:
```bash
docker compose ps postgres
docker compose exec postgres pg_isready -U tsr_user -d tsr_db
```

### API health check fails

Check API logs:
```bash
docker compose logs api
```

Common issues:
- Database not ready (wait for health check)
- Missing dependencies (rebuild image)
- Port 5000 already in use

### Port conflicts

If port 5000, 5432, or 6379 is already in use, modify docker-compose.yml:
```yaml
ports:
  - "5001:5000"  # Change host port
```

## Success Criteria

✅ All services start and show "healthy" status
✅ API responds at http://localhost:5000/api/tsr/stats
✅ Database tables created successfully
✅ Test data seeded (3+ TSRs)
✅ ChromaDB initialized with documents
✅ Monitoring baselines configured
✅ Web interfaces accessible
✅ Logs show no errors
✅ CI workflow runs successfully
✅ Data persists across restarts (volumes)

## Next Steps

After successful local testing:

1. **Commit Changes**: If you modified any files, commit them
2. **Push to GitHub**: Push to trigger CI/CD workflow
3. **Monitor CI Build**: Check GitHub Actions for successful build
4. **Review TSR Report**: Download TSR artifact from workflow
5. **Production Deployment**: Follow deployment guide (when ready)

## Notes

- First startup takes longer due to image building and dependency installation
- Subsequent starts are much faster (uses cached images)
- Volumes persist data across restarts
- Use `docker compose down -v` for a completely fresh start
- CI configuration uses tmpfs for faster tests (no disk I/O)
