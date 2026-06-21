import pytest
from unittest.mock import AsyncMock, patch

from backend.graph.state import AgentState


def make_state(**overrides) -> AgentState:
    base: AgentState = {
        "workflow_id": "test-wf-1",
        "user_query": "Prepare weekly report and suggest priorities for next week",
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
    base.update(overrides)
    return base


@pytest.mark.asyncio
async def test_supervisor_node_returns_goal_and_agents():
    mock_output = {
        "goal": "prepare_weekly_report",
        "required_agents": ["planner", "knowledge", "analytics", "decision"],
    }
    with patch("backend.agents.supervisor.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        from backend.agents.supervisor import supervisor_node
        result = await supervisor_node(make_state())
    assert result["goal"] == "prepare_weekly_report"
    assert "planner" in result["required_agents"]
    assert result["status"] == "running"
    assert len(result["agent_logs"]) == 1
    assert result["agent_logs"][0]["agent"] == "supervisor"


@pytest.mark.asyncio
async def test_planner_node_returns_tasks():
    mock_output = {
        "tasks": ["collect_data", "analyze_performance", "identify_risks", "generate_recommendations"]
    }
    with patch("backend.agents.planner.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        from backend.agents.planner import planner_node
        result = await planner_node(make_state(goal="prepare_weekly_report"))
    assert len(result["tasks"]) >= 1
    assert isinstance(result["tasks"][0], str)
    assert result["agent_logs"][0]["agent"] == "planner"


@pytest.mark.asyncio
async def test_knowledge_node_returns_documents():
    with patch("backend.agents.knowledge.retrieve") as mock_retrieve:
        mock_retrieve.return_value = [{"content": "Project Beta at risk", "metadata": {}}]
        from backend.agents.knowledge import knowledge_node
        result = await knowledge_node(make_state(goal="prepare_weekly_report", tasks=["collect_data"]))
    assert isinstance(result["documents"], list)
    assert result["documents"][0]["content"] == "Project Beta at risk"
    assert result["agent_logs"][0]["agent"] == "knowledge"


@pytest.mark.asyncio
async def test_analytics_node_returns_insights_and_risks():
    mock_output = {
        "kpis": {"on_track": 3, "at_risk": 2},
        "risks": [{"project": "Project Beta", "risk_level": "High", "reason": "Missing developers"}],
        "insights": {"summary": "Team below velocity target", "key_finding": "Resource constraints"},
    }
    with patch("backend.agents.analytics.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        from backend.agents.analytics import analytics_node
        result = await analytics_node(make_state(
            goal="prepare_weekly_report",
            tasks=["collect_data", "analyze"],
            documents=[{"content": "Project Beta at risk", "metadata": {}}],
        ))
    assert isinstance(result["insights"], dict)
    assert len(result["risks"]) >= 1
    assert result["agent_logs"][0]["agent"] == "analytics"


@pytest.mark.asyncio
async def test_decision_node_returns_recommendations():
    mock_output = {
        "recommendations": [
            "Allocate 2 engineers to Project Beta",
            "Review scope of Project Gamma with client",
        ]
    }
    with patch("backend.agents.decision.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(return_value=mock_output)
        from backend.agents.decision import decision_node
        result = await decision_node(make_state(
            goal="prepare_weekly_report",
            insights={"summary": "Below target"},
            risks=[{"project": "Project Beta", "risk_level": "High", "reason": "Missing devs"}],
        ))
    assert len(result["recommendations"]) >= 1
    assert result["status"] == "waiting_approval"
    assert result["agent_logs"][0]["agent"] == "decision"


@pytest.mark.asyncio
async def test_executor_node_returns_markdown_report():
    with patch("backend.agents.executor.chain") as mock_chain:
        mock_chain.ainvoke = AsyncMock(
            return_value="# Weekly Operations Report\n\n## Executive Summary\nTeam below target."
        )
        from backend.agents.executor import executor_node
        result = await executor_node(make_state(
            goal="prepare_weekly_report",
            insights={"summary": "Below target", "key_finding": "Resource issues"},
            risks=[{"project": "Beta", "risk_level": "High", "reason": "Missing devs"}],
            recommendations=["Allocate 2 engineers to Beta"],
            approved=True,
        ))
    assert "# Weekly Operations Report" in result["execution_result"]
    assert result["status"] == "completed"
    assert result["agent_logs"][0]["agent"] == "executor"
