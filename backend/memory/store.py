import json
from collections import defaultdict

import asyncpg

from backend.config import settings


async def _get_conn() -> asyncpg.Connection:
    return await asyncpg.connect(settings.DATABASE_URL_ASYNC)


async def save_memory(key: str, value: dict) -> None:
    conn = await _get_conn()
    try:
        await conn.execute(
            """
            INSERT INTO memory_store (key, value, updated_at)
            VALUES ($1, $2::jsonb, NOW())
            ON CONFLICT (key) DO UPDATE SET value = $2::jsonb, updated_at = NOW()
            """,
            key,
            json.dumps(value),
        )
    finally:
        await conn.close()


async def load_memory(key: str) -> dict | None:
    conn = await _get_conn()
    try:
        row = await conn.fetchrow("SELECT value FROM memory_store WHERE key = $1", key)
        return json.loads(row["value"]) if row else None
    finally:
        await conn.close()


async def load_recent_memories(limit: int = 10) -> list[dict]:
    conn = await _get_conn()
    try:
        rows = await conn.fetch(
            "SELECT key, value, updated_at FROM memory_store ORDER BY updated_at DESC LIMIT $1",
            limit,
        )
        return [
            {
                "key": r["key"],
                "value": json.loads(r["value"]),
                "updated_at": str(r["updated_at"]),
            }
            for r in rows
        ]
    finally:
        await conn.close()


async def load_memory_by_prefix(prefix: str, limit: int = 20) -> list[dict]:
    conn = await _get_conn()
    try:
        rows = await conn.fetch(
            """
            SELECT key, value, updated_at FROM memory_store
            WHERE key LIKE $1
            ORDER BY updated_at DESC LIMIT $2
            """,
            f"{prefix}:%",
            limit,
        )
        return [
            {
                "key": r["key"],
                "value": json.loads(r["value"]),
                "updated_at": str(r["updated_at"]),
            }
            for r in rows
        ]
    finally:
        await conn.close()


async def save_entity_memory(entity_key: str, data: dict) -> None:
    """Upsert entity memory, merging list fields (sessions) rather than overwriting."""
    existing = await load_memory(f"entity_memory:{entity_key}") or {}
    # Merge session list
    sessions = list(set(existing.get("sessions", []) + data.get("sessions", [])))
    merged = {**existing, **data, "sessions": sessions}
    await save_memory(f"entity_memory:{entity_key}", merged)


async def load_feedback_stats() -> dict:
    """Aggregate all feedback_history records into stats."""
    records = await load_memory_by_prefix("feedback_history", limit=200)
    total = len(records)
    helpful = sum(1 for r in records if r["value"].get("rating") == "helpful")
    not_helpful = total - helpful

    # Count by goal type from workflow_history linked by session_id
    return {
        "total_feedbacks": total,
        "helpful": helpful,
        "not_helpful": not_helpful,
        "helpful_rate": round(helpful / total * 100) if total > 0 else 0,
    }


async def load_recent_feedback_for_goal(goal_prefix: str, limit: int = 5) -> list[dict]:
    """Load recent feedback records where the session's goal matches (best-effort)."""
    records = await load_memory_by_prefix("feedback_history", limit=50)
    # Filter by goal prefix match (goal stored in recommendation_history, linked by session_id)
    matched = []
    for r in records:
        sid = r["value"].get("session_id", "")
        rec = await load_memory(f"recommendation_history:{sid}")
        if rec and goal_prefix and goal_prefix.split("_")[0] in rec.get("goal", ""):
            matched.append({
                "goal": rec.get("goal", ""),
                "rating": r["value"].get("rating", ""),
                "confidence": rec.get("confidence", 0.0),
            })
        if len(matched) >= limit:
            break
    return matched
