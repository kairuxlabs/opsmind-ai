from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.routes.workflow import _registry
from backend.graph.workflow import workflow as lg_workflow
from backend.observability.tracker import log_agent_event

router = APIRouter()


class ApprovalRequest(BaseModel):
    approved: bool
    comment: str = ""


@router.post("/workflow/{workflow_id}/approval")
async def submit_approval(workflow_id: str, body: ApprovalRequest):
    if workflow_id not in _registry:
        raise HTTPException(status_code=404, detail="Workflow not found")

    config = _registry[workflow_id]

    if not body.approved:
        lg_workflow.update_state(config, {"status": "rejected", "approved": False})
        return {"workflow_id": workflow_id, "status": "rejected"}

    lg_workflow.update_state(config, {"approved": True, "status": "executing"})
    await lg_workflow.ainvoke(None, config=config)

    state = lg_workflow.get_state(config)
    current = state.values

    for log in current.get("agent_logs", []):
        if log["agent"] in ("executor", "memory"):
            try:
                await log_agent_event(
                    workflow_id=workflow_id,
                    agent_name=log["agent"],
                    latency_ms=log["latency_ms"],
                    output=log["output"],
                )
            except Exception:
                pass

    return {
        "workflow_id": workflow_id,
        "status": current.get("status", "completed"),
        "execution_result": current.get("execution_result", ""),
        "confidence": current.get("confidence", 0.0),
        "explanation": current.get("explanation", []),
        "health_score": current.get("health_score", 0),
    }
