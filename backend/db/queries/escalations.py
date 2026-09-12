"""Queries against escalations."""
import asyncpg


async def list_open_escalations(conn: asyncpg.Connection, business_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(
        """
        SELECT * FROM escalations
        WHERE business_id = $1 AND resolved_at IS NULL
        ORDER BY created_at DESC
        """,
        business_id,
    )


async def count_open_escalations(conn: asyncpg.Connection, business_id: str) -> int:
    row = await conn.fetchrow(
        """
        SELECT COUNT(*) AS n FROM escalations
        WHERE business_id = $1 AND resolved_at IS NULL
        """,
        business_id,
    )
    return row["n"]
