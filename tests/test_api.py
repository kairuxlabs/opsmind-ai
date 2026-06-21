import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from httpx import AsyncClient, ASGITransport

from backend.api.main import app


@pytest.mark.asyncio
async def test_create_workflow_returns_workflow_id():
    # POST now returns immediately (status: "starting") — workflow runs in background
    with patch("backend.api.routes.workflow.write_workflow", new_callable=AsyncMock), \
         patch("backend.api.routes.workflow._run_workflow_streaming", new_callable=AsyncMock):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post("/api/workflow", json={"request": "Prepare weekly report"})

    assert resp.status_code == 200
    data = resp.json()
    assert "workflow_id" in data
    assert data["status"] == "starting"
    assert data["goal"] == ""
    assert data["route"] == []


@pytest.mark.asyncio
async def test_submit_feedback_helpful():
    with patch("backend.api.routes.feedback.load_memory", new_callable=AsyncMock) as mock_load, \
         patch("backend.api.routes.feedback.save_memory", new_callable=AsyncMock):
        mock_load.return_value = None
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/workflow/nonexistent-id/feedback",
                json={"rating": "helpful"},
            )
    assert resp.status_code == 200
    data = resp.json()
    assert data["feedback"] == "helpful"
    assert data["recorded"] is True


@pytest.mark.asyncio
async def test_submit_feedback_invalid_rating():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/api/workflow/some-id/feedback",
            json={"rating": "unknown"},
        )
    assert resp.status_code == 422


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
