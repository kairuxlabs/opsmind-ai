from backend.graph.state import AgentState


def test_agent_state_has_required_fields():
    state: AgentState = {
        "session_id": "test-123",
        "user_query": "Prepare weekly report",
        "goal": "",
        "route": [],
        "tasks": [],
        "documents": [],
        "insights": {},
        "risks": [],
        "recommendations": [],
        "confidence": 0.0,
        "explanation": [],
        "health_score": 0,
        "critique": None,
        "approved": False,
        "feedback": None,
        "execution_result": "",
        "status": "planning",
        "agent_logs": [],
        "created_at": "2026-06-21T00:00:00Z",
        "error": None,
    }
    assert state["session_id"] == "test-123"
    assert state["status"] == "planning"
    assert isinstance(state["tasks"], list)
    assert isinstance(state["risks"], list)
    assert isinstance(state["insights"], dict)
    assert isinstance(state["route"], list)
    assert isinstance(state["explanation"], list)
    assert state["confidence"] == 0.0
    assert state["health_score"] == 0
    assert state["critique"] is None
    assert state["approved"] is False
    assert state["feedback"] is None
