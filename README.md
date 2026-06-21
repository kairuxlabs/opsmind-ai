# OpsMind AI v2.0

> **An Autonomous Multi-Agent Decision Intelligence Platform**
>
> Transforming Data → Decisions → Actions with AI Digital Teammates

## Overview

OpsMind AI is a multi-agent AI system that helps enterprise teams:
- Analyze work status and detect risks automatically
- Generate data-driven recommendations
- Enforce human approval before execution
- Produce structured operations reports

### Demo Flow

```
Input: "Prepare weekly report and suggest priorities for next week"

✓ Supervisor  — Understand request & assign agents
✓ Planner     — Generate workflow tasks
✓ Knowledge   — Retrieve relevant context (RAG / pgvector)
✓ Analytics   — Extract KPIs and identify risks
✓ Decision    — Generate actionable recommendations
⏳ Human      — Review & approve via dashboard
✓ Executor    — Generate final Markdown report
✓ Memory      — Save to long-term memory (PostgreSQL)
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI / Agents | LangGraph + DeepSeek V3 |
| Backend | FastAPI (Python 3.11) |
| Frontend | React 18 + Vite + Tailwind CSS |
| Database | PostgreSQL 16 + pgvector |
| RAG Embeddings | sentence-transformers (all-MiniLM-L6-v2, local) |
| Deployment | Docker Compose |

## Quick Start (Docker)

**Prerequisites:** Docker Desktop, DeepSeek API key ([platform.deepseek.com](https://platform.deepseek.com))

```bash
git clone https://github.com/<your-username>/opsmind-ai
cd opsmind-ai

cp .env.example .env
# Edit .env and set DEEPSEEK_API_KEY=<your key>

cd docker && docker compose up --build
```

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

## Local Development

```bash
# 1. Start PostgreSQL
cd docker && docker compose up -d postgres && cd ..

# 2. Backend
pip install -r requirements.txt
cp .env.example .env   # fill in DEEPSEEK_API_KEY
python main.py         # hot-reload on http://localhost:8000

# 3. Ingest sample data
python -c "import asyncio; from backend.rag.ingest import ingest_csv; asyncio.run(ingest_csv('data/sample/project_data.csv'))"

# 4. Frontend
cd frontend && npm install && npm run dev  # http://localhost:3000

# 5. Tests
cd .. && pytest tests/ -v
```

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/workflow` | Create and start workflow |
| GET | `/api/workflow/{id}` | Get workflow status and full state |
| POST | `/api/workflow/{id}/approval` | Approve or reject workflow |
| GET | `/api/metrics` | Observability metrics |
| POST | `/api/ingest` | Upload CSV/TXT file for RAG |

### Example

```bash
# Start a workflow
curl -X POST http://localhost:8000/api/workflow \
  -H "Content-Type: application/json" \
  -d '{"request": "Prepare weekly report and suggest priorities for next week"}'

# Returns: {"workflow_id": "...", "status": "waiting_approval"}

# Approve it
curl -X POST http://localhost:8000/api/workflow/<id>/approval \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
```

## Architecture

```
User → FastAPI → LangGraph StateGraph
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
      Supervisor    Planner     Knowledge
          │
      Analytics → Decision
                      │
              Human Approval ⏳
                      │
                  Executor → Memory
                      │
                  Dashboard
```

### Key files

| File | Responsibility |
|------|---------------|
| `backend/graph/state.py` | `AgentState` TypedDict — all agent I/O contracts |
| `backend/graph/workflow.py` | LangGraph StateGraph, `interrupt_before=["executor"]` |
| `backend/agents/` | 7 agent nodes |
| `backend/rag/` | pgvector ingest + semantic retrieve |
| `backend/api/routes/` | FastAPI routes + in-memory workflow registry |
| `frontend/src/api/client.js` | All API calls (Axios) |

## Scope (MVP)

In scope: FastAPI backend, LangGraph multi-agent workflow, pgvector RAG, human approval, React dashboard, Docker Compose.

Out of scope: Kubernetes, Kafka, Redis, microservices, Slack/Jira integrations, mobile app, multi-user auth, model fine-tuning.
