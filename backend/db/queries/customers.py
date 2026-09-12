"""Queries against customers and customer_memories."""
import asyncpg


async def get_or_create_customer(
    conn: asyncpg.Connection, business_id: str, phone_number: str, display_name: str | None
) -> asyncpg.Record:
    existing = await conn.fetchrow(
        "SELECT * FROM customers WHERE business_id = $1 AND phone_number = $2",
        business_id,
        phone_number,
    )
    if existing:
        return await conn.fetchrow(
            """
            UPDATE customers SET last_seen_at = NOW(),
                display_name = COALESCE(customers.display_name, $3)
            WHERE id = $1 AND business_id = $2
            RETURNING *
            """,
            existing["id"],
            business_id,
            display_name,
        )
    return await conn.fetchrow(
        """
        INSERT INTO customers (business_id, phone_number, display_name)
        VALUES ($1, $2, $3)
        RETURNING *
        """,
        business_id,
        phone_number,
        display_name,
    )


async def get_memories(conn: asyncpg.Connection, customer_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(
        "SELECT * FROM customer_memories WHERE customer_id = $1 ORDER BY created_at",
        customer_id,
    )


async def delete_memory(conn: asyncpg.Connection, customer_id: str, memory_id: str) -> bool:
    result = await conn.execute(
        "DELETE FROM customer_memories WHERE id = $1 AND customer_id = $2",
        memory_id,
        customer_id,
    )
    return result.endswith(" 1")
