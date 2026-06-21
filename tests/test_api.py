import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from backend.api.main import app


@pytest.mark.asyncio
async def test_create_workflow_returns_workflow_id():
    mock_state = MagicMock()
    mock_state.values = {
        "status": "waiting_approval",
        "goal": "prepare_weekly_report",
        "tasks": ["collect_data"],
        "insights": {},
        "risks": [],
        "recommendations": ["Allocate engineers"],
        "agent_logs": [],
        "execution_result": "",
        "user_query": "Prepare weekly report",
    }
    with patch("backend.api.routes.workflow.lg_workflow") as mock_wf:
        mock_wf.ainvoke = AsyncMock(return_value=None)
        mock_wf.get_state = MagicMock(return_value=mock_state)

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/workflow", json={"request": "Prepare weekly report"})

    assert resp.status_code == 200
    data = resp.json()
    assert "workflow_id" in data
    assert data["status"] == "waiting_approval"


@pytest.mark.asyncio
async def test_get_metrics_returns_dict():
    with patch("backend.api.routes.workflow.get_system_metrics", new_callable=AsyncMock) as mock_m:
        mock_m.return_value = {
            "workflows_today": 5,
            "avg_latency_ms": 1200,
            "human_approvals": 3,
            "risks_detected": 2,
        }
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/metrics")
    assert resp.status_code == 200
    assert "workflows_today" in resp.json()


@pytest.mark.asyncio
async def test_get_workflow_not_found():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/api/workflow/nonexistent-id")
    assert resp.status_code == 404
