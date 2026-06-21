import uuid

import pytest
from unittest.mock import AsyncMock, patch

from backend.graph.workflow import workflow
from backend.graph.state import AgentState


@pytest.mark.asyncio
async def test_workflow_runs_to_interrupt():
    wf_id = str(uuid.uuid4())
    initial: AgentState = {
        "workflow_id": wf_id,
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
    config = {"configurable": {"thread_id": wf_id}}

    supervisor_out = {
        "goal": "prepare_weekly_report",
        "required_agents": ["planner", "knowledge", "analytics", "decision"],
    }
    planner_out = {"tasks": ["collect_data", "analyze", "recommend"]}
    knowledge_out = [{"content": "Project Beta at risk", "metadata": {}}]
    analytics_out = {
        "kpis": {"on_track": 3, "at_risk": 2},
        "risks": [{"project": "Beta", "risk_level": "High", "reason": "Missing devs"}],
        "insights": {"summary": "Below target", "key_finding": "Resource issues"},
    }
    decision_out = {"recommendations": ["Allocate engineers to Beta"]}

    with (
        patch("backend.agents.supervisor.chain") as s,
        patch("backend.agents.planner.chain") as p,
        patch("backend.agents.knowledge.retrieve", new_callable=AsyncMock) as k,
        patch("backend.agents.analytics.chain") as an,
        patch("backend.agents.decision.chain") as d,
    ):
        s.ainvoke = AsyncMock(return_value=supervisor_out)
        p.ainvoke = AsyncMock(return_value=planner_out)
        k.return_value = knowledge_out
        an.ainvoke = AsyncMock(return_value=analytics_out)
        d.ainvoke = AsyncMock(return_value=decision_out)

        await workflow.ainvoke(initial, config=config)

    state = workflow.get_state(config)
    assert state.values["status"] == "waiting_approval"
    assert state.values["goal"] == "prepare_weekly_report"
    assert len(state.values["recommendations"]) >= 1
    assert len(state.values["agent_logs"]) == 5  # supervisor, planner, knowledge, analytics, decision
