from typing import Optional, TypedDict


class AgentState(TypedDict):
    session_id: str
    user_query: str
    goal: str
    route: list[str]             # dynamic agent list from supervisor
    tasks: list[str]
    documents: list[dict]
    insights: dict
    risks: list[dict]
    recommendations: list[dict]  # [{text: str, reasons: list[str]}]
    confidence: float            # recommendation confidence 0.0-1.0
    explanation: list[str]       # overall reasoning summary
    health_score: int            # enterprise health score 0-100
    critique: Optional[dict]     # {consistency, issues, suggestions, critique_passed, adjusted_confidence}
    approved: bool
    feedback: Optional[str]      # "helpful" | "not_helpful"
    execution_result: str
    status: str                  # planning | running | waiting_approval | executing | completed | failed | rejected
    agent_logs: list[dict]       # [{agent, latency_ms, output}]
    created_at: str
    error: Optional[str]
