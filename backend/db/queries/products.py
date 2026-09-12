"""Queries against products (read-side, for dashboard use)."""
import asyncpg


async def list_products(conn: asyncpg.Connection, business_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(
        "SELECT * FROM products WHERE business_id = $1 AND is_active = TRUE ORDER BY name",
        business_id,
    )


async def find_product_by_name(
    conn: asyncpg.Connection, business_id: str, name: str
) -> asyncpg.Record | None:
    return await conn.fetchrow(
        """
        SELECT * FROM products
        WHERE business_id = $1 AND is_active = TRUE AND name ILIKE '%' || $2 || '%'
        LIMIT 1
        """,
        business_id,
        name,
    )
