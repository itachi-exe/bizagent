"""Queries against conversations and messages."""
import asyncpg


async def message_exists(conn: asyncpg.Connection, wamid: str) -> bool:
    row = await conn.fetchrow("SELECT 1 FROM messages WHERE wamid = $1", wamid)
    return row is not None


async def get_or_create_active_conversation(
    conn: asyncpg.Connection, business_id: str, customer_id: str
) -> asyncpg.Record:
    existing = await conn.fetchrow(
        """
        SELECT * FROM conversations
        WHERE customer_id = $1 AND status = 'active'
        ORDER BY started_at DESC LIMIT 1
        """,
        customer_id,
    )
    if existing:
        return existing
    return await conn.fetchrow(
        """
        INSERT INTO conversations (business_id, customer_id)
        VALUES ($1, $2)
        RETURNING *
        """,
        business_id,
        customer_id,
    )


async def touch_conversation(conn: asyncpg.Connection, conversation_id: str) -> None:
    await conn.execute(
        "UPDATE conversations SET last_message_at = NOW() WHERE id = $1", conversation_id
    )


async def insert_message(
    conn: asyncpg.Connection,
    conversation_id: str,
    wamid: str | None,
    role: str,
    content: str,
) -> asyncpg.Record:
    return await conn.fetchrow(
        """
        INSERT INTO messages (conversation_id, wamid, role, content)
        VALUES ($1, $2, $3, $4)
        RETURNING *
        """,
        conversation_id,
        wamid,
        role,
        content,
    )


async def list_conversations(conn: asyncpg.Connection, business_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(
        """
        SELECT
            c.id,
            c.status,
            c.outcome,
            c.last_message_at,
            cu.display_name AS customer_name,
            cu.phone_number AS customer_phone,
            (
                SELECT m.content FROM messages m
                WHERE m.conversation_id = c.id
                ORDER BY m.sent_at DESC LIMIT 1
            ) AS last_message_preview
        FROM conversations c
        JOIN customers cu ON cu.id = c.customer_id
        WHERE c.business_id = $1
        ORDER BY c.last_message_at DESC
        """,
        business_id,
    )


async def set_outcome(conn: asyncpg.Connection, conversation_id: str, outcome: str) -> bool:
    result = await conn.execute(
        """
        UPDATE conversations SET outcome = $2, outcome_set_at = NOW()
        WHERE id = $1
        """,
        conversation_id,
        outcome,
    )
    return result.endswith(" 1")


async def add_feedback(conn: asyncpg.Connection, message_id: str, signal: str) -> asyncpg.Record:
    return await conn.fetchrow(
        """
        INSERT INTO message_feedback (message_id, signal)
        VALUES ($1, $2)
        RETURNING *
        """,
        message_id,
        signal,
    )
