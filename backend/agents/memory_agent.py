import time
from datetime import datetime, timezone

from backend.graph.state import AgentState
from backend.memory.store import save_memory


async def memory_node(state: AgentState) -> dict:
    start = time.time()
    session_id = state["session_id"]
    now = datetime.now(timezone.utc).isoformat()

    # Workflow history — full record of this execution
    await save_memory(f"workflow_history:{session_id}", {
        "session_id": session_id,
        "query": state["user_query"],
        "goal": state["goal"],
        "route": state.get("route", []),
        "status": state.get("status", "completed"),
        "approved": state.get("approved", False),
        "execution_result": state.get("execution_result", ""),
        "timestamp": now,
    })

    # Recommendation history — for future context and feedback tracking
    if state.get("recommendations"):
        await save_memory(f"recommendation_history:{session_id}", {
            "session_id": session_id,
            "goal": state["goal"],
            "recommendations": state.get("recommendations", []),
            "confidence": state.get("confidence", 0.0),
            "explanation": state.get("explanation", []),
            "feedback": state.get("feedback"),
            "timestamp": now,
        })

    latency = int((time.time() - start) * 1000)
    log = {"agent": "memory", "latency_ms": latency, "output": {"saved_session": session_id}}
    return {"agent_logs": state.get("agent_logs", []) + [log]}
