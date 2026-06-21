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


def _build_workflow():
    builder = StateGraph(AgentState)

    builder.add_node("supervisor", supervisor_node)
    builder.add_node("planner", planner_node)
    builder.add_node("knowledge", knowledge_node)
    builder.add_node("analytics", analytics_node)
    builder.add_node("decision", decision_node)
    builder.add_node("executor", executor_node)
    builder.add_node("memory", memory_node)

    builder.set_entry_point("supervisor")
    builder.add_edge("supervisor", "planner")
    builder.add_edge("planner", "knowledge")
    builder.add_edge("knowledge", "analytics")
    builder.add_edge("analytics", "decision")
    builder.add_edge("decision", "executor")
    builder.add_edge("executor", "memory")
    builder.add_edge("memory", END)

    checkpointer = MemorySaver()
    return builder.compile(
        checkpointer=checkpointer,
        interrupt_before=["executor"],
    )


workflow = _build_workflow()
