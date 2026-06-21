from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph

from backend.agents.analytics import analytics_node
from backend.agents.decision import decision_node
from backend.agents.executor import executor_node
from backend.agents.knowledge import knowledge_node
from backend.agents.memory_agent import memory_node
from backend.agents.planner import planner_node
from backend.agents.supervisor import supervisor_node
from backend.graph.state import AgentState

# Agents that participate in dynamic routing (supervisor decides order)
_ROUTABLE = {"planner", "knowledge", "analytics", "decision"}


def _next_agent(state: AgentState) -> str:
    """Pick the next unrun agent from the supervisor's route list."""
    route = state.get("route", [])
    run_agents = {log["agent"] for log in state.get("agent_logs", [])}
    for agent in route:
        if agent in _ROUTABLE and agent not in run_agents:
            return agent
    # All routable agents done — supervisor may have skipped decision; go there anyway
    return "decision"


def _build_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("planner", planner_node)
    builder.add_node("knowledge", knowledge_node)
    builder.add_node("analytics", analytics_node)
    builder.add_node("decision", decision_node)
    builder.add_node("executor", executor_node)
    builder.add_node("memory", memory_node)

    _route_map = {
        "planner": "planner",
        "knowledge": "knowledge",
        "analytics": "analytics",
        "decision": "decision",
    }

    # After supervisor: route to first agent in the dynamic list
    builder.set_entry_point("supervisor")
    builder.add_conditional_edges("supervisor", _next_agent, _route_map)

    # After each routable agent: pick next unrun agent from route
    for node in ("planner", "knowledge", "analytics"):
        builder.add_conditional_edges(node, _next_agent, _route_map)

    # Decision → human approval gate → executor → memory → end
    builder.add_edge("decision", "executor")
    builder.add_edge("executor", "memory")
    builder.add_edge("memory", END)

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["executor"],
    )


workflow = _build_workflow()
