import importlib
import time

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Minimal default state for playground testing
_DEFAULT_STATE = {
    "session_id": "playground",
    "user_query": "",
    "goal": "quick_analysis",
    "route": ["knowledge", "analytics", "decision"],
    "tasks": [
        "collect_project_status_data",
        "analyze_performance_metrics",
        "identify_risks_and_blockers",
        "generate_recommendations",
    ],
    "documents": [],
    "insights": {
        "summary": "Team is operating below velocity target with 2 projects at risk",
        "key_finding": "Resource constraints are the primary driver of project delays",
    },
    "risks": [
        {"project": "Project Alpha", "risk_level": "High", "reason": "Missing 2 developers since May"},
        {"project": "Project Beta", "risk_level": "Medium", "reason": "Scope changes mid-sprint"},
    ],
    "recommendations": [
        {
            "text": "Allocate 2 additional engineers to Project Alpha immediately",
            "reasons": ["Completion rate 52% vs 75% target", "Resource gap confirmed in HR report"],
        }
    ],
    "confidence": 0.75,
    "explanation": ["Project Alpha at critical risk due to resource shortage"],
    "health_score": 72,
    "critique": None,
    "approved": False,
    "feedback": None,
    "execution_result": "",
    "status": "running",
    "agent_logs": [],
    "created_at": "2026-06-21T00:00:00Z",
    "error": None,
}

_AGENT_MAP: dict[str, tuple[str, str]] = {
    "supervisor": ("supervisor_node", "backend.agents.supervisor"),
    "planner": ("planner_node", "backend.agents.planner"),
    "analytics": ("analytics_node", "backend.agents.analytics"),
    "decision": ("decision_node", "backend.agents.decision"),
    "critique": ("critique_node", "backend.agents.critique"),
}


class PlaygroundRequest(BaseModel):
    agent: str
    query: str


@router.post("/playground")
async def run_playground(body: PlaygroundRequest):
    if body.agent not in _AGENT_MAP:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown agent '{body.agent}'. Available: {list(_AGENT_MAP.keys())}",
        )

    fn_name, module_path = _AGENT_MAP[body.agent]
    module = importlib.import_module(module_path)
    agent_fn = getattr(module, fn_name)

    state = {**_DEFAULT_STATE, "user_query": body.query}

    start = time.time()
    result = await agent_fn(state)
    latency_ms = int((time.time() - start) * 1000)

    # Exclude agent_logs from output — not useful in playground context
    output = {k: v for k, v in result.items() if k != "agent_logs"}

    return {
        "agent": body.agent,
        "query": body.query,
        "output": output,
        "latency_ms": latency_ms,
    }
