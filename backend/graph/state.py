from typing import Optional, TypedDict


class AgentState(TypedDict):
    session_id: str
    user_query: str
    goal: str
    route: list[str]          # dynamic agent list from supervisor
    tasks: list[str]
    documents: list[dict]
    insights: dict
    risks: list[dict]
    recommendations: list[str]
    confidence: float          # FR-04: recommendation confidence 0.0-1.0
    explanation: list[str]     # FR-05: reasoning behind decisions
    health_score: int          # FR-07: enterprise health score 0-100
    approved: bool
    feedback: Optional[str]    # FR-06: "helpful" | "not_helpful"
    execution_result: str
    status: str                # planning | running | waiting_approval | executing | completed | failed | rejected
    agent_logs: list[dict]     # [{agent, latency_ms, output}]
    created_at: str
    error: Optional[str]
