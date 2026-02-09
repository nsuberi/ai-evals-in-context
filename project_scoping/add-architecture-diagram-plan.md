# Plan: Add Architecture Diagram to README

## Summary
Add Mermaid architecture diagrams to `/ai-testing-resource/README.md` covering both local Docker Compose and AWS production deployments.

## File to Modify
`/ai-testing-resource/README.md` - Insert new "## Architecture" section after "## Features" (after line 15)

## Changes

### Add Architecture Section with Two Mermaid Diagrams

**1. Local Development (Docker Compose) Diagram:**
```mermaid
flowchart TB
    subgraph Browser
        User[User Browser]
    end

    subgraph Docker["Docker Compose Network"]
        API[Flask API<br/>:5001]
        PG[(PostgreSQL<br/>:5432)]
        Redis[(Redis<br/>:6379)]
        Chroma[(Chroma<br/>Vector DB)]
    end

    subgraph External
        Anthropic[Anthropic<br/>Claude API]
    end

    User -->|HTTP| API
    API -->|TSR Data| PG
    API -->|WebSocket Queue| Redis
    API -->|RAG Embeddings| Chroma
    API -->|AI Requests| Anthropic
```

**2. AWS Production Diagram:**
```mermaid
flowchart TB
    subgraph Internet
        User[User Browser]
    end

    subgraph AWS["AWS (us-east-1)"]
        subgraph Public["Public Subnet"]
            ALB[Application<br/>Load Balancer]
            ECS[ECS Fargate<br/>Flask Container]
        end

        subgraph Private["Private Subnet"]
            RDS[(RDS PostgreSQL)]
        end

        subgraph Services["AWS Services"]
            ECR[ECR<br/>Image Registry]
            Secrets[Secrets Manager]
            CW[CloudWatch<br/>Logs]
        end
    end

    subgraph External
        Anthropic[Anthropic<br/>Claude API]
    end

    User -->|HTTPS| ALB
    ALB -->|Routes| ECS
    ECS -->|SQL| RDS
    ECS -->|Credentials| Secrets
    ECS -->|Logs| CW
    ECR -->|Image Pull| ECS
    ECS -->|AI Requests| Anthropic
```

**3. Brief component descriptions:**
- Local: PostgreSQL for TSR storage, Redis for WebSocket pub/sub, Chroma for RAG
- AWS: ECS Fargate with Spot instances, ALB for HTTPS, RDS in private subnet

## Verification
1. View the modified README on GitHub to confirm Mermaid diagrams render
2. Cross-check diagram components against `docker-compose.yml` and `terraform/main.tf`
