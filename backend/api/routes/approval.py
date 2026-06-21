from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.routes.workflow import _registry
from backend.graph.workflow import workflow as lg_workflow
from backend.observability.tracker import log_agent_event, update_workflow_status

router = APIRouter()


class ApprovalRequest(BaseModel):
    approved: bool
    comment: str = ""
    modified_recommendations: list[dict] | None = None


@router.post("/workflow/{workflow_id}/approval")
async def submit_approval(workflow_id: str, body: ApprovalRequest):
    if workflow_id not in _registry:
        raise HTTPException(status_code=404, detail="Workflow not found")

    config = _registry[workflow_id]

    if not body.approved:
        lg_workflow.update_state(config, {"status": "rejected", "approved": False})
        try:
            await update_workflow_status(workflow_id, "rejected")
        except Exception:
            pass
        return {"workflow_id": workflow_id, "status": "rejected"}

    state_update: dict = {"approved": True, "status": "executing"}
    if body.modified_recommendations is not None:
        # Normalise: ensure each item has text + reasons shape
        state_update["recommendations"] = [
            r if isinstance(r, dict) and "text" in r else {"text": str(r), "reasons": []}
            for r in body.modified_recommendations
        ]
    lg_workflow.update_state(config, state_update)
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

    final_status = current.get("status", "completed")
    try:
        await update_workflow_status(workflow_id, final_status)
    except Exception:
        pass

    return {
        "workflow_id": workflow_id,
        "status": current.get("status", "completed"),
        "execution_result": current.get("execution_result", ""),
        "confidence": current.get("confidence", 0.0),
        "explanation": current.get("explanation", []),
        "health_score": current.get("health_score", 0),
        "critique": current.get("critique"),
    }
