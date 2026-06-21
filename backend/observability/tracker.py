import json
from datetime import datetime, timezone

import asyncpg

from backend.config import settings
from backend.services.tracing import langfuse_enabled


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


async def write_workflow(workflow_id: str, user_query: str) -> None:
    conn = await _get_conn()
    try:
        await conn.execute(
            """
            INSERT INTO workflows (id, user_query, status)
            VALUES ($1::uuid, $2, 'planning')
            ON CONFLICT (id) DO NOTHING
            """,
            workflow_id,
            user_query,
        )
    finally:
        await conn.close()


async def update_workflow_status(workflow_id: str, status: str) -> None:
    conn = await _get_conn()
    try:
        await conn.execute(
            """
            UPDATE workflows SET status = $2, updated_at = NOW() WHERE id = $1::uuid
            """,
            workflow_id,
            status,
        )
    finally:
        await conn.close()


async def get_metrics_history(days: int = 7) -> list[dict]:
    """Return per-day counts for the last N days."""
    conn = await _get_conn()
    try:
        rows = await conn.fetch(
            """
            SELECT
                created_at::date AS day,
                COUNT(*) AS total,
                COUNT(*) FILTER (WHERE status = 'completed') AS completed,
                COUNT(*) FILTER (WHERE status = 'failed') AS failed,
                COALESCE(AVG(
                    EXTRACT(EPOCH FROM (updated_at - created_at)) * 1000
                )::int, 0) AS avg_ms
            FROM workflows
            WHERE created_at >= NOW() - ($1 || ' days')::interval
            GROUP BY day
            ORDER BY day
            """,
            str(days),
        )
        return [
            {
                "date": str(r["day"]),
                "total": int(r["total"]),
                "completed": int(r["completed"]),
                "failed": int(r["failed"]),
                "avg_latency_ms": int(r["avg_ms"]),
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
        completed = await conn.fetchval(
            "SELECT COUNT(*) FROM workflows WHERE status = 'completed' AND created_at::date = $1::date",
            today,
        )
        failed = await conn.fetchval(
            "SELECT COUNT(*) FROM workflows WHERE status = 'failed' AND created_at::date = $1::date",
            today,
        )
        rejected = await conn.fetchval(
            "SELECT COUNT(*) FROM workflows WHERE status = 'rejected' AND created_at::date = $1::date",
            today,
        )
        avg_latency = await conn.fetchval(
            "SELECT AVG(latency_ms) FROM agent_logs WHERE started_at::date = $1::date", today
        )

        # Count risks detected from agent_logs output (analytics agent outputs risks array)
        risks_row = await conn.fetchval(
            """
            SELECT COUNT(*)
            FROM agent_logs
            WHERE agent_name = 'analytics'
              AND started_at::date = $1::date
              AND jsonb_array_length(output->'risks') > 0
            """,
            today,
        )

        total = int(workflows_today or 0)
        done = int(completed or 0)
        err = int(failed or 0)

        success_rate = round(done / total * 100) if total > 0 else 0
        error_rate = round(err / total * 100) if total > 0 else 0
        approval_rate = round(done / (done + int(rejected or 0)) * 100) if (done + int(rejected or 0)) > 0 else 0

        return {
            "workflows_today": total,
            "avg_latency_ms": int(avg_latency or 0),
            "human_approvals": done,
            "risks_detected": int(risks_row or 0),
            "success_rate": success_rate,
            "error_rate": error_rate,
            "approval_rate": approval_rate,
            "langfuse_enabled": langfuse_enabled(),
            "langfuse_host": settings.LANGFUSE_HOST if langfuse_enabled() else None,
        }
    finally:
        await conn.close()
