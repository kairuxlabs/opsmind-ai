import os
import tempfile
import uuid
from datetime import datetime, timezone

import aiofiles
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.graph.state import AgentState
from backend.graph.workflow import workflow as lg_workflow
from backend.observability.tracker import get_system_metrics, log_agent_event
from backend.rag.ingest import ingest_csv, ingest_text

router = APIRouter()

# In-memory registry: workflow_id -> LangGraph config thread
# For production: replace with a database-backed registry
_registry: dict[str, dict] = {}


class WorkflowRequest(BaseModel):
    request: str


@router.post("/workflow")
async def create_workflow(body: WorkflowRequest):
    workflow_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": workflow_id}}

    initial: AgentState = {
        "workflow_id": workflow_id,
        "user_query": body.request,
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
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error": None,
    }

    await lg_workflow.ainvoke(initial, config=config)

    state = lg_workflow.get_state(config)
    current = state.values

    for log in current.get("agent_logs", []):
        try:
            await log_agent_event(
                workflow_id=workflow_id,
                agent_name=log["agent"],
                latency_ms=log["latency_ms"],
                output=log["output"],
            )
        except Exception:
            pass  # Observability failures must not block the response

    _registry[workflow_id] = config
    return {"workflow_id": workflow_id, "status": current.get("status", "waiting_approval")}


@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    if workflow_id not in _registry:
        raise HTTPException(status_code=404, detail="Workflow not found")
    config = _registry[workflow_id]
    state = lg_workflow.get_state(config)
    current = state.values
    return {
        "workflow_id": workflow_id,
        "status": current.get("status"),
        "user_query": current.get("user_query"),
        "goal": current.get("goal"),
        "tasks": current.get("tasks", []),
        "insights": current.get("insights", {}),
        "risks": current.get("risks", []),
        "recommendations": current.get("recommendations", []),
        "agent_logs": current.get("agent_logs", []),
        "execution_result": current.get("execution_result", ""),
        "created_at": current.get("created_at"),
    }


@router.get("/metrics")
async def get_metrics():
    try:
        return await get_system_metrics()
    except Exception:
        return {"workflows_today": 0, "avg_latency_ms": 0, "human_approvals": 0, "risks_detected": 0}


@router.post("/ingest")
async def ingest_file(file: UploadFile = File(...)):
    suffix = os.path.splitext(file.filename or "upload.txt")[1].lower()
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp_path = tmp.name
    try:
        async with aiofiles.open(tmp_path, "wb") as f:
            await f.write(await file.read())
        count = await ingest_csv(tmp_path) if suffix == ".csv" else await ingest_text(tmp_path)
    finally:
        os.unlink(tmp_path)
    return {"ingested": count, "filename": file.filename}
