import time
from datetime import datetime, timezone

from backend.graph.state import AgentState
from backend.memory.store import load_memory, save_entity_memory, save_memory


async def memory_node(state: AgentState) -> dict:
    start = time.time()
    session_id = state["session_id"]
    now = datetime.now(timezone.utc).isoformat()
    goal = state.get("goal", "")

    # 1. Workflow history — full record of this execution
    await save_memory(f"workflow_history:{session_id}", {
        "session_id": session_id,
        "query": state["user_query"],
        "goal": goal,
        "route": state.get("route", []),
        "status": state.get("status", "completed"),
        "approved": state.get("approved", False),
        "execution_result": state.get("execution_result", ""),
        "health_score": state.get("health_score", 0),
        "timestamp": now,
    })

    # 2. Recommendation history — for future context and feedback tracking
    if state.get("recommendations"):
        await save_memory(f"recommendation_history:{session_id}", {
            "session_id": session_id,
            "goal": goal,
            "recommendations": state.get("recommendations", []),
            "confidence": state.get("confidence", 0.0),
            "explanation": state.get("explanation", []),
            "critique_passed": state.get("critique", {}).get("critique_passed") if state.get("critique") else None,
            "feedback": state.get("feedback"),
            "timestamp": now,
        })

    # 3. Entity memory — extract project entities from risks
    for risk in state.get("risks", []):
        project = risk.get("project", "").strip()
        if project:
            safe_key = project.lower().replace(" ", "_")
            await save_entity_memory(f"project:{safe_key}", {
                "project": project,
                "last_risk_level": risk.get("risk_level", "Unknown"),
                "last_reason": risk.get("reason", ""),
                "last_seen_goal": goal,
                "last_seen": now,
                "sessions": [session_id],
            })

    # 4. User preferences — track goal frequency and approval patterns
    prefs = await load_memory("user_preferences:global") or {
        "goal_counts": {},
        "total_workflows": 0,
        "total_approved": 0,
        "approval_rate": 0,
    }
    goal_counts = prefs.get("goal_counts", {})
    goal_type = goal.split("_")[0] if goal else "unknown"
    goal_counts[goal_type] = goal_counts.get(goal_type, 0) + 1

    total = prefs.get("total_workflows", 0) + 1
    total_approved = prefs.get("total_approved", 0) + (1 if state.get("approved") else 0)

    await save_memory("user_preferences:global", {
        "goal_counts": goal_counts,
        "total_workflows": total,
        "total_approved": total_approved,
        "approval_rate": round(total_approved / total * 100) if total > 0 else 0,
        "last_updated": now,
    })

    latency = int((time.time() - start) * 1000)
    log = {"agent": "memory", "latency_ms": latency, "output": {
        "saved_session": session_id,
        "entities_extracted": len(state.get("risks", [])),
    }}
    return {"agent_logs": state.get("agent_logs", []) + [log]}
