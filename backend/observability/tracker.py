import json
from datetime import datetime, timezone

import asyncpg

from backend.config import settings


async def _get_conn() -> asyncpg.Connection:
    return await asyncpg.connect(settings.DATABASE_URL_ASYNC)


async def log_agent_event(
    workflow_id: str,
    agent_name: str,
    latency_ms: int,
    output: dict,
    error: str | None = None,
) -> None:
    conn = await _get_conn()
    try:
        await conn.execute(
            """
            INSERT INTO agent_logs (workflow_id, agent_name, latency_ms, output, error)
            VALUES ($1, $2, $3, $4::jsonb, $5)
            """,
            workflow_id,
            agent_name,
            latency_ms,
            json.dumps(output),
            error,
        )
    finally:
        await conn.close()


async def get_workflow_logs(workflow_id: str) -> list[dict]:
    conn = await _get_conn()
    try:
        rows = await conn.fetch(
            "SELECT agent_name, latency_ms, output, error FROM agent_logs WHERE workflow_id = $1 ORDER BY id",
            workflow_id,
        )
        return [
            {
                "agent": r["agent_name"],
                "latency_ms": r["latency_ms"],
                "output": json.loads(r["output"]),
                "error": r["error"],
            }
            for r in rows
        ]
    finally:
        await conn.close()


async def get_system_metrics() -> dict:
    conn = await _get_conn()
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        workflows_today = await conn.fetchval(
            "SELECT COUNT(*) FROM workflows WHERE created_at::date = $1::date", today
        )
        avg_latency = await conn.fetchval(
            "SELECT AVG(latency_ms) FROM agent_logs WHERE started_at::date = $1::date", today
        )
        approvals = await conn.fetchval(
            "SELECT COUNT(*) FROM workflows WHERE status = 'completed' AND created_at::date = $1::date",
            today,
        )
        return {
            "workflows_today": int(workflows_today or 0),
            "avg_latency_ms": int(avg_latency or 0),
            "human_approvals": int(approvals or 0),
            "risks_detected": 0,
        }
    finally:
        await conn.close()
