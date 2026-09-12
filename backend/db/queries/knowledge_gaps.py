"""Queries against knowledge_gaps."""
import asyncpg


async def list_open_gaps(conn: asyncpg.Connection, business_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(
        """
        SELECT * FROM knowledge_gaps
        WHERE business_id = $1 AND resolved = FALSE
        ORDER BY created_at DESC
        """,
        business_id,
    )


async def resolve_gap(
    conn: asyncpg.Connection, gap_id: str, resolved: bool, resolution: str | None
) -> asyncpg.Record | None:
    return await conn.fetchrow(
        """
        UPDATE knowledge_gaps SET
            resolved = $2,
            resolution = $3,
            resolved_at = CASE WHEN $2 THEN NOW() ELSE resolved_at END
        WHERE id = $1
        RETURNING *
        """,
        gap_id,
        resolved,
        resolution,
    )
