<h1 align="center">
  <br>
  ⚡ OpsMind AI
  <br>
</h1>

<h4 align="center">Autonomous Multi-Agent Decision Intelligence Platform</h4>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/LangGraph-0.2-FF6B35?style=flat" />
  <img src="https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black" />
  <img src="https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat&logo=postgresql&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat" />
</p>

<p align="center">
  <a href="#overview">Overview</a> •
  <a href="#features">Features</a> •
  <a href="#tech-stack">Tech Stack</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#local-development">Local Dev</a> •
  <a href="#api-reference">API</a> •
  <a href="#architecture">Architecture</a> •
  <a href="#contributing">Contributing</a>
</p>

---

## Overview

OpsMind AI is an open-source autonomous decision-intelligence platform that transforms natural-language requests into structured operational reports — with a mandatory human review gate before any action is taken.

A user submits a plain-English request (e.g. *"Prepare weekly status and suggest priorities"*). Eight specialized AI agents collaborate in a LangGraph state-machine pipeline, retrieving relevant context from a vector database, analyzing KPIs and risks, generating confidence-scored recommendations, and critiquing their own output for consistency. The workflow pauses for human approval before the Executor produces a final Markdown report. Every step is logged with latency metrics and optionally traced in Langfuse.

```
"Prepare weekly report and suggest priorities for next week"

  ✓ Supervisor   — understand intent, select agents dynamically
  ✓ Planner      — decompose goal into ordered tasks
  ✓ Knowledge    — hybrid RAG retrieval (pgvector + cross-encoder re-ranking)
  ✓ Analytics    — extract KPIs, detect risks, score enterprise health
  ✓ Decision     — generate confidence-scored recommendations
  ✓ Critique     — self-review for consistency, flag issues
  ⏳ Human       — review risks, recommendations, and approve via dashboard
  ✓ Executor     — generate structured Markdown operations report
  ✓ Memory       — persist workflow to PostgreSQL long-term memory
```

---

## Features

### Agent Pipeline
- **Dynamic Routing** — Supervisor selects only the agents required for each request
- **Hybrid RAG** — pgvector similarity search with reciprocal rank fusion (RRF) and cross-encoder re-ranking (`ms-marco-MiniLM-L-6-v2`)
- **Explainability** — every workflow carries a confidence score (0–100), enterprise health score, and a human-readable reasoning chain
- **Critique Agent** — reviews Decision output for logical consistency before surfacing recommendations to the human approver
- **Human-in-the-Loop** — mandatory approval gate via `LangGraph interrupt_before`; operators can edit recommendations before approving
- **Long-term Memory** — completed workflows are saved to PostgreSQL and retrievable across sessions

### Infrastructure
- **SSE Streaming** — real-time agent progress events (`/api/workflow/{id}/events`) streamed to the dashboard
- **Feedback Learning** — thumbs-up/down on completed workflows feeds a `feedback` column for future fine-tuning
- **PDF Ingestion** — upload PDF, CSV, or TXT documents into the knowledge base via `/api/ingest`
- **Langfuse Tracing** — optional LLM observability (traces, costs, latency) — enabled by adding keys to `.env`
- **Docker Compose** — one-command full-stack deployment

### Dashboard (React)
| Page | Purpose |
|------|---------|
| Command Center | Submit requests, view recent workflows, quick-start templates, export reports |
| Workflow View | Real-time agent pipeline with SSE, approval UI, final report |
| Playground | Interactive agent testing environment |
| Insights | Agent performance analytics — latency tiers, success rates, approval rates |
| Memory Center | Browse long-term memory entries |
| Observability | System metrics, 7-day workflow history chart |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agents | [LangGraph](https://github.com/langchain-ai/langgraph) 0.2 + DeepSeek V3 |
| LLM API | DeepSeek V3 (`deepseek-chat`) via OpenAI-compatible endpoint |
| Backend | [FastAPI](https://fastapi.tiangolo.com/) 0.115 (Python 3.11, fully async) |
| Frontend | React 18 + Vite 6 + Tailwind CSS 3 |
| Database | PostgreSQL 16 + [pgvector](https://github.com/pgvector/pgvector) |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2` (384-dim, local — no API key) |
| Re-ranking | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local) |
| Observability | [Langfuse](https://langfuse.com/) (optional) + custom `agent_logs` table |
| Deployment | Docker Compose |

---

## Quick Start

**Prerequisites:** [Docker Desktop](https://www.docker.com/products/docker-desktop/), a [DeepSeek API key](https://platform.deepseek.com)

```bash
git clone https://github.com/kairuxlabs/opsmind-ai.git
cd opsmind-ai

cp .env.example .env
# Open .env and set DEEPSEEK_API_KEY=<your-key>

cd docker && docker compose up --build
```

| Service | URL |
|---------|-----|
| Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| Swagger UI | http://localhost:8000/docs |

After the stack is up, ingest the sample dataset:

```bash
docker compose exec backend python -c \
  "import asyncio; from backend.rag.ingest import ingest_csv; asyncio.run(ingest_csv('data/sample/project_data.csv'))"
```

Then open http://localhost:3000, type a request, and watch the agents work.

---

## Local Development

### 1. PostgreSQL

```bash
cd docker && docker compose up -d postgres && cd ..
```

### 2. Backend

```bash
pip install -r requirements.txt
cp .env.example .env   # fill in DEEPSEEK_API_KEY
python main.py         # http://localhost:8000, hot-reload enabled
```

### 3. Ingest sample data

```bash
python -c "import asyncio; from backend.rag.ingest import ingest_csv; asyncio.run(ingest_csv('data/sample/project_data.csv'))"
```

### 4. Frontend

```bash
cd frontend && npm install && npm run dev   # http://localhost:3000
```

### 5. Tests

```bash
pytest tests/ -v
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in the values.

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DEEPSEEK_API_KEY` | **Yes** | — | DeepSeek V3 API key |
| `DATABASE_URL` | No | `postgresql+psycopg://postgres:postgres@localhost:5432/opsmind` | Sync connection (LangChain/pgvector) |
| `DATABASE_URL_ASYNC` | No | `postgresql://postgres:postgres@localhost:5432/opsmind` | Async connection (asyncpg) |
| `EMBEDDING_MODEL` | No | `all-MiniLM-L6-v2` | HuggingFace embedding model |
| `RERANKER_MODEL` | No | `cross-encoder/ms-marco-MiniLM-L-6-v2` | Cross-encoder re-ranking model |
| `LANGFUSE_PUBLIC_KEY` | No | — | Langfuse public key (leave blank to disable tracing) |
| `LANGFUSE_SECRET_KEY` | No | — | Langfuse secret key |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse host URL |

---

## API Reference

### Workflow

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/workflow` | Create and start a workflow |
| `GET` | `/api/workflow/{id}` | Get workflow state (live or archived fallback) |
| `GET` | `/api/workflow/{id}/events` | SSE stream — real-time agent events |
| `GET` | `/api/workflows` | List recent workflows (default: 20) |
| `POST` | `/api/workflow/{id}/approval` | Approve or reject a workflow |

### Knowledge & Data

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/ingest` | Upload CSV, TXT, or PDF for RAG ingestion |

### Observability & Feedback

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/metrics` | System metrics (workflows today, avg latency, approvals) |
| `GET` | `/api/metrics/history` | 7-day daily workflow counts |
| `GET` | `/api/insights` | Agent performance analytics (latency, success rate) |
| `POST` | `/api/workflow/{id}/feedback` | Submit thumbs-up/down feedback |

### Playground

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/playground/run` | Test individual agents interactively |

### Example: run a workflow end-to-end

```bash
# 1. Start a workflow
curl -X POST http://localhost:8000/api/workflow \
  -H "Content-Type: application/json" \
  -d '{"request": "Prepare weekly report and suggest priorities for next week"}'
# → {"workflow_id": "abc-123", "status": "starting"}

# 2. Poll until waiting_approval
curl http://localhost:8000/api/workflow/abc-123

# 3. Approve
curl -X POST http://localhost:8000/api/workflow/abc-123/approval \
  -H "Content-Type: application/json" \
  -d '{"approved": true}'
# → {"status": "completed", "execution_result": "# Weekly Operations Report ..."}
```

---

## Architecture

```
Browser
  │
  ▼
React Dashboard (Vite + Tailwind)
  │  REST + SSE
  ▼
FastAPI  ──────────────────────────────────────────────────────┐
  │                                                            │
  │  POST /api/workflow                                        │
  ▼                                                            │
LangGraph StateGraph                                           │
  │                                                            │
  ├── Supervisor  →  selects dynamic agent route              │
  ├── Planner     →  decomposes goal into tasks               │
  ├── Knowledge   →  hybrid RAG (pgvector + RRF + reranker)   │
  ├── Analytics   →  KPIs, risks, health score                │
  ├── Decision    →  confidence-scored recommendations         │
  ├── Critique    →  consistency self-review                   │
  │                                                            │
  │   interrupt_before=["executor"]  ←── Human Approval Gate  │
  │                                                            │
  ├── Executor    →  Markdown operations report               │
  └── Memory      →  persist to PostgreSQL                    │
                                                              │
PostgreSQL 16 + pgvector ─────────────────────────────────────┘
  ├── langchain_pg_embedding  (RAG document store)
  ├── workflows               (workflow history)
  ├── agent_logs              (per-agent latency + output)
  └── memory_store            (long-term key-value memory)
```

### Key files

| File | Responsibility |
|------|---------------|
| `backend/graph/state.py` | `AgentState` TypedDict — single source of truth for all agent I/O |
| `backend/graph/workflow.py` | LangGraph `StateGraph` assembly, `interrupt_before=["executor"]` |
| `backend/agents/` | 8 async agent nodes |
| `backend/rag/retrieve.py` | Hybrid retrieval: pgvector + RRF + cross-encoder re-ranking |
| `backend/rag/ingest.py` | CSV / TXT / PDF ingestion into pgvector |
| `backend/observability/tracker.py` | Writes `agent_logs` and `workflows` tables; computes metrics |
| `backend/services/tracing.py` | Optional Langfuse callback injection |
| `backend/api/routes/workflow.py` | `_registry` dict (session → LangGraph config), SSE generator |
| `frontend/src/api/client.js` | All API calls (Axios); Vite proxies `/api` → port 8000 |

---

## Project Structure

```
opsmind-ai/
├── backend/
│   ├── agents/          # supervisor, planner, knowledge, analytics,
│   │                    # critique, decision, executor, memory_agent
│   ├── graph/
│   │   ├── state.py     # AgentState TypedDict
│   │   └── workflow.py  # LangGraph StateGraph
│   ├── rag/
│   │   ├── ingest.py    # CSV / TXT / PDF → pgvector
│   │   └── retrieve.py  # hybrid retrieval + re-ranking
│   ├── memory/
│   │   └── store.py     # asyncpg CRUD for memory_store
│   ├── observability/
│   │   └── tracker.py   # agent_logs + metrics queries
│   ├── services/
│   │   └── tracing.py   # Langfuse integration
│   ├── api/
│   │   ├── main.py      # FastAPI app + CORS
│   │   └── routes/      # workflow, approval, feedback, playground
│   └── config.py        # pydantic-settings
├── frontend/
│   └── src/
│       ├── components/  # Dashboard, WorkflowView, HumanApproval,
│       │                # AgentTimeline, Playground, Insights,
│       │                # MemoryCenter, Observability, AgentMonitor
│       └── api/
│           └── client.js
├── docker/
│   ├── docker-compose.yml
│   ├── init.sql         # pgvector extension + schema
│   ├── Dockerfile.backend
│   └── Dockerfile.frontend
├── tests/               # pytest — state, agents, workflow, API (16 tests)
├── data/sample/         # project_data.csv for demo ingestion
├── requirements.txt
├── .env.example
└── main.py              # uvicorn entry point
```

---

## Contributing

Contributions are welcome. Please follow these steps:

1. **Fork** the repo and create a branch: `git checkout -b feat/your-feature`
2. **Set up locally** using the [Local Development](#local-development) steps
3. **Write tests** for any new behaviour — run `pytest tests/ -v` before submitting
4. **Keep agent changes async** — all backend code uses `async def`
5. **Open a PR** with a clear description of what changed and why

### Reporting bugs

Open an issue with:
- The request text you submitted
- The workflow ID (from the dashboard URL)
- The full error from the API response or browser console

### Adding a new agent

1. Create `backend/agents/your_agent.py` — implement `async def your_agent_node(state: AgentState) -> dict`
2. Register the node in `backend/graph/workflow.py` and wire the edge
3. Add the agent name to `AGENTS` in `frontend/src/components/AgentMonitor.jsx`
4. Add a test in `tests/test_agents.py` following the existing mock pattern

---

## Acknowledgements

- [LangGraph](https://github.com/langchain-ai/langgraph) — stateful multi-agent orchestration with human-in-the-loop support
- [DeepSeek](https://platform.deepseek.com) — LLM powering all agent reasoning (OpenAI-compatible API)
- [pgvector](https://github.com/pgvector/pgvector) — vector similarity search for PostgreSQL
- [sentence-transformers](https://www.sbert.net/) — local embedding and cross-encoder re-ranking models
- [Langfuse](https://langfuse.com/) — open-source LLM observability and tracing

---

## License

[MIT](LICENSE) © 2026 OpsMind AI
