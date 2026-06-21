import uuid

import pytest
from unittest.mock import AsyncMock, patch

from backend.graph.workflow import workflow
from backend.graph.state import AgentState


@pytest.mark.asyncio
async def test_workflow_runs_to_interrupt():
    session_id = str(uuid.uuid4())
    initial: AgentState = {
        "session_id": session_id,
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
    config = {"configurable": {"thread_id": session_id}}

    supervisor_out = {
        "goal": "prepare_weekly_report",
        "route": ["planner", "knowledge", "analytics", "decision"],
    }
    planner_out = {"tasks": ["collect_data", "analyze", "recommend"]}
    knowledge_out = [{"content": "Project Beta at risk", "metadata": {}}]
    analytics_out = {
        "kpis": {"on_track": 3, "at_risk": 2},
        "risks": [{"project": "Beta", "risk_level": "High", "reason": "Missing devs"}],
        "insights": {"summary": "Below target", "key_finding": "Resource issues"},
        "health_score": 68,
    }
    decision_out = {
        "recommendations": [
            {
                "text": "Allocate engineers to Beta immediately",
                "reasons": ["Beta completion at 52%", "Resource gap since May"],
            }
        ],
        "confidence": 0.85,
        "explanation": ["Beta completion at 52%", "Resource gap is primary driver"],
    }

    critique_out = {
        "consistency": True,
        "critique_passed": True,
        "adjusted_confidence": 0.87,
        "issues": [],
        "suggestions": ["Add timelines to recommendations"],
    }

    with (
        patch("backend.agents.supervisor.chain") as s,
        patch("backend.agents.planner.chain") as p,
        patch("backend.agents.knowledge.retrieve", new_callable=AsyncMock) as k,
        patch("backend.agents.analytics.chain") as an,
        patch("backend.agents.decision.chain") as d,
        patch("backend.agents.critique.chain") as cr,
    ):
        s.ainvoke = AsyncMock(return_value=supervisor_out)
        p.ainvoke = AsyncMock(return_value=planner_out)
        k.return_value = knowledge_out
        an.ainvoke = AsyncMock(return_value=analytics_out)
        d.ainvoke = AsyncMock(return_value=decision_out)
        cr.ainvoke = AsyncMock(return_value=critique_out)

        await workflow.ainvoke(initial, config=config)

    state = workflow.get_state(config)
    vals = state.values
    assert vals["status"] == "waiting_approval"
    assert vals["goal"] == "prepare_weekly_report"
    assert vals["route"] == ["planner", "knowledge", "analytics", "decision"]
    assert len(vals["recommendations"]) >= 1
    assert isinstance(vals["recommendations"][0], dict)
    assert "text" in vals["recommendations"][0]
    assert vals["confidence"] == 0.87  # adjusted by critique
    assert len(vals["explanation"]) >= 1
    assert vals["health_score"] == 68
    assert vals["critique"] is not None
    assert vals["critique"]["critique_passed"] is True
    assert len(vals["agent_logs"]) == 6  # supervisor, planner, knowledge, analytics, decision, critique
