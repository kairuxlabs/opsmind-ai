import json

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
