import time

from backend.graph.state import AgentState
from backend.memory.store import save_memory


async def memory_node(state: AgentState) -> dict:
    start = time.time()
    key = f"workflow:{state['workflow_id']}"
    await save_memory(key, {
        "query": state["user_query"],
        "goal": state["goal"],
        "recommendations": state.get("recommendations", []),
        "risks": state.get("risks", []),
        "execution_result": state.get("execution_result", ""),
        "approved": state.get("approved", False),
    })
    latency = int((time.time() - start) * 1000)
    log = {"agent": "memory", "latency_ms": latency, "output": {"saved_key": key}}
    return {"agent_logs": state.get("agent_logs", []) + [log]}
