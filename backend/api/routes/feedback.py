from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.routes.workflow import _registry
from backend.graph.workflow import workflow as lg_workflow
from backend.memory.store import load_memory, load_recent_memories, save_memory

router = APIRouter()


class FeedbackRequest(BaseModel):
    rating: str  # "helpful" | "not_helpful"


@router.post("/workflow/{workflow_id}/feedback")
async def submit_feedback(workflow_id: str, body: FeedbackRequest):
    if body.rating not in ("helpful", "not_helpful"):
        raise HTTPException(status_code=422, detail="rating must be 'helpful' or 'not_helpful'")

    # Update live workflow state if still in registry
    if workflow_id in _registry:
        config = _registry[workflow_id]
        lg_workflow.update_state(config, {"feedback": body.rating})

    # Persist feedback to memory store
    key = f"feedback_history:{workflow_id}"
    existing = await load_memory(key) or {}
    existing.update({
        "session_id": workflow_id,
        "rating": body.rating,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    try:
        await save_memory(key, existing)
    except Exception:
        pass  # DB unavailable must not block response

    return {"workflow_id": workflow_id, "feedback": body.rating, "recorded": True}


@router.get("/memory")
async def get_memory_history(limit: int = 20):
    try:
        records = await load_recent_memories(limit)
        return {"records": records, "count": len(records)}
    except Exception:
        return {"records": [], "count": 0}
