"""Queries against the uploads table (Business Brain population)."""
import json

import asyncpg


async def create_upload(
    conn: asyncpg.Connection, business_id: str, filename: str, file_type: str, extracted_data: dict
) -> asyncpg.Record:
    return await conn.fetchrow(
        """
        INSERT INTO uploads (business_id, filename, file_type, extracted_data)
        VALUES ($1, $2, $3, $4::jsonb)
        RETURNING *
        """,
        business_id,
        filename,
        file_type,
        json.dumps(extracted_data),
    )


async def get_upload(conn: asyncpg.Connection, upload_id: str) -> asyncpg.Record | None:
    return await conn.fetchrow("SELECT * FROM uploads WHERE id = $1", upload_id)


async def mark_confirmed(conn: asyncpg.Connection, upload_id: str) -> None:
    await conn.execute(
        "UPDATE uploads SET confirmed_at = NOW() WHERE id = $1", upload_id
    )
