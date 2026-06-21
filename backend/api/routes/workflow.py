import os
import tempfile
import uuid
from datetime import datetime, timezone

import aiofiles
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from pydantic import BaseModel

from backend.graph.state import AgentState
from backend.graph.workflow import workflow as lg_workflow
from backend.observability.tracker import (
    get_system_metrics,
    log_agent_event,
    update_workflow_status,
    write_workflow,
)
from backend.rag.ingest import ingest_csv, ingest_text

router = APIRouter()

# In-memory registry: session_id -> LangGraph config thread
_registry: dict[str, dict] = {}


class WorkflowRequest(BaseModel):
    request: str


async def _run_workflow_streaming(session_id: str, initial: AgentState, config: dict) -> None:
    """Background task: streams each agent node via LangGraph astream, logs to DB incrementally."""
    seen_agents: set[str] = set()
    try:
        async for state in lg_workflow.astream(initial, config=config, stream_mode="values"):
            for log in state.get("agent_logs", []):
                agent = log["agent"]
                if agent not in seen_agents:
                    seen_agents.add(agent)
                    try:
                        await log_agent_event(
                            workflow_id=session_id,
                            agent_name=agent,
                            latency_ms=log["latency_ms"],
                            output=log["output"],
                        )
                    except Exception:
                        pass
    except Exception:
        pass

    # Workflow reached interrupt (waiting_approval) — update DB status
    try:
        final = lg_workflow.get_state(config)
        status = final.values.get("status", "waiting_approval") if final and final.values else "waiting_approval"
        await update_workflow_status(session_id, status)
    except Exception:
        pass


@router.post("/workflow")
async def create_workflow(body: WorkflowRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": session_id}}

    initial: AgentState = {
        "session_id": session_id,
        "user_query": body.request,
        "goal": "",
        "route": [],
        "tasks": [],
        "documents": [],
        "insights": {},
        "risks": [],
        "recommendations": [],
        "confidence": 0.0,
        "explanation": [],
        "health_score": 0,
        "critique": None,
        "approved": False,
        "feedback": None,
        "execution_result": "",
        "status": "starting",
        "agent_logs": [],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error": None,
    }

    try:
        await write_workflow(session_id, body.request)
    except Exception:
        pass

    # Register before task starts so GET can find this workflow immediately
    _registry[session_id] = config
    background_tasks.add_task(_run_workflow_streaming, session_id, initial, config)

    return {
        "workflow_id": session_id,
        "status": "starting",
        "goal": "",
        "route": [],
    }


@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    if workflow_id not in _registry:
        raise HTTPException(status_code=404, detail="Workflow not found")
    config = _registry[workflow_id]
    state = lg_workflow.get_state(config)

    # State may be empty if background task hasn't committed the first node yet
    current = state.values if (state and state.values) else {}
    if not current:
        return {
            "workflow_id": workflow_id,
            "status": "starting",
            "user_query": "",
            "goal": "",
            "route": [],
            "tasks": [],
            "insights": {},
            "risks": [],
            "recommendations": [],
            "confidence": 0.0,
            "explanation": [],
            "health_score": 0,
            "critique": None,
            "agent_logs": [],
            "execution_result": "",
            "feedback": None,
            "created_at": None,
        }

    return {
        "workflow_id": workflow_id,
        "status": current.get("status"),
        "user_query": current.get("user_query"),
        "goal": current.get("goal"),
        "route": current.get("route", []),
        "tasks": current.get("tasks", []),
        "insights": current.get("insights", {}),
        "risks": current.get("risks", []),
        "recommendations": current.get("recommendations", []),
        "confidence": current.get("confidence", 0.0),
        "explanation": current.get("explanation", []),
        "health_score": current.get("health_score", 0),
        "critique": current.get("critique"),
        "agent_logs": current.get("agent_logs", []),
        "execution_result": current.get("execution_result", ""),
        "feedback": current.get("feedback"),
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
