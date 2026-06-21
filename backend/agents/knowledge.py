import time

from backend.graph.state import AgentState
from backend.rag.retrieve import retrieve


async def knowledge_node(state: AgentState) -> dict:
    start = time.time()
    query = f"{state['goal']} {' '.join(state.get('tasks', [])[:3])}"
    documents = await retrieve(query, k=5)
    latency = int((time.time() - start) * 1000)
    log = {"agent": "knowledge", "latency_ms": latency, "output": {"retrieved": len(documents)}}
    return {
        "documents": documents,
        "agent_logs": state.get("agent_logs", []) + [log],
    }
