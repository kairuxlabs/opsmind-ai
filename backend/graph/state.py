from typing import Optional, TypedDict


class AgentState(TypedDict):
    workflow_id: str
    user_query: str
    goal: str
    required_agents: list[str]
    tasks: list[str]
    documents: list[dict]
    insights: dict
    risks: list[dict]
    recommendations: list[str]
    approved: bool
    execution_result: str
    status: str  # planning | running | waiting_approval | executing | completed | failed | rejected
    agent_logs: list[dict]  # [{agent, latency_ms, output}]
    created_at: str
    error: Optional[str]
