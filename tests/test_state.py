from backend.graph.state import AgentState


def test_agent_state_has_required_fields():
    state: AgentState = {
        "workflow_id": "test-123",
        "user_query": "Prepare weekly report",
        "goal": "",
        "required_agents": [],
        "tasks": [],
        "documents": [],
        "insights": {},
        "risks": [],
        "recommendations": [],
        "approved": False,
        "execution_result": "",
        "status": "planning",
        "agent_logs": [],
        "created_at": "2026-06-21T00:00:00Z",
        "error": None,
    }
    assert state["workflow_id"] == "test-123"
    assert state["status"] == "planning"
    assert isinstance(state["tasks"], list)
    assert isinstance(state["risks"], list)
    assert isinstance(state["insights"], dict)
    assert state["approved"] is False
