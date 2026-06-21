import os

# Set required env vars before any backend imports so Settings() can instantiate
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key-for-testing")
os.environ.setdefault("DATABASE_URL", "postgresql+psycopg://postgres:postgres@localhost:5432/opsmind")
os.environ.setdefault("DATABASE_URL_ASYNC", "postgresql://postgres:postgres@localhost:5432/opsmind")

import pytest


@pytest.fixture
def sample_state():
    return {
        "workflow_id": "test-integration-1",
        "user_query": "Prepare weekly report and suggest priorities for next week",
        "goal": "",
        "required_agents": [],
        "tasks": [],
        "documents": [],
        "insights": {},
        "risks": [],
        "recommendations": [],
        "approved": False,
        "execution_result": "",
        "status": "planning",
        "agent_logs": [],
        "created_at": "2026-06-21T00:00:00Z",
        "error": None,
    }
