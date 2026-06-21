from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.routes.workflow import _registry
from backend.graph.workflow import workflow as lg_workflow
from backend.memory.store import (
    load_feedback_stats,
    load_memory,
    load_memory_by_prefix,
    load_recent_memories,
    save_memory,
)

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
        pass

    return {"workflow_id": workflow_id, "feedback": body.rating, "recorded": True}


@router.get("/memory")
async def get_memory_history(limit: int = 20):
    try:
        records = await load_recent_memories(limit)
        return {"records": records, "count": len(records)}
    except Exception:
        return {"records": [], "count": 0}


@router.get("/memory/stats")
async def get_memory_stats():
    try:
        feedback_stats = await load_feedback_stats()
        prefs = await load_memory("user_preferences:global") or {}
        entities = await load_memory_by_prefix("entity_memory", limit=100)
        return {
            "total_workflows": prefs.get("total_workflows", 0),
            "total_approved": prefs.get("total_approved", 0),
            "approval_rate": prefs.get("approval_rate", 0),
            "goal_counts": prefs.get("goal_counts", {}),
            "total_feedbacks": feedback_stats["total_feedbacks"],
            "helpful": feedback_stats["helpful"],
            "not_helpful": feedback_stats["not_helpful"],
            "helpful_rate": feedback_stats["helpful_rate"],
            "entities_tracked": len(entities),
        }
    except Exception:
        return {
            "total_workflows": 0, "total_approved": 0, "approval_rate": 0,
            "goal_counts": {}, "total_feedbacks": 0, "helpful": 0,
            "not_helpful": 0, "helpful_rate": 0, "entities_tracked": 0,
        }


@router.get("/memory/entities")
async def get_entity_memories(limit: int = 20):
    try:
        records = await load_memory_by_prefix("entity_memory", limit=limit)
        return {"records": records, "count": len(records)}
    except Exception:
        return {"records": [], "count": 0}


@router.get("/memory/feedback")
async def get_feedback_history(limit: int = 20):
    try:
        records = await load_memory_by_prefix("feedback_history", limit=limit)
        stats = await load_feedback_stats()
        return {"records": records, "count": len(records), "stats": stats}
    except Exception:
        return {"records": [], "count": 0, "stats": {}}
