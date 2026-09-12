"""Conversation context is rebuilt from PostgreSQL for every incoming message."""

from db.connection import get_pool


async def load_history(conversation_id: str, limit: int = 10) -> list[dict]:
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch("""SELECT role, content FROM messages
                                   WHERE conversation_id=$1
                                   ORDER BY created_at DESC LIMIT $2""", conversation_id, limit)
    role_map = {"customer": "user", "user": "user", "agent": "assistant", "assistant": "assistant"}
    return [
        {"role": role_map.get(row["role"], "user"), "content": row["content"]}
        for row in reversed(rows)
    ]
