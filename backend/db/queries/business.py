"""Queries against businesses, products, services, policies, agent_permissions, business_brain_extended."""
import asyncpg


async def get_business(conn: asyncpg.Connection, business_id: str) -> asyncpg.Record | None:
    return await conn.fetchrow("SELECT * FROM businesses WHERE id = $1", business_id)


async def get_bot_settings(conn: asyncpg.Connection, business_id: str) -> asyncpg.Record | None:
    return await conn.fetchrow(
        """
        SELECT agent_name, agent_personality, agent_greeting, agent_language_style
        FROM businesses WHERE id = $1
        """,
        business_id,
    )


async def update_bot_settings(
    conn: asyncpg.Connection,
    business_id: str,
    agent_name: str | None,
    agent_personality: str | None,
    agent_greeting: str | None,
    agent_language_style: str | None,
) -> asyncpg.Record:
    return await conn.fetchrow(
        """
        UPDATE businesses SET
            agent_name = COALESCE($2, agent_name),
            agent_personality = COALESCE($3, agent_personality),
            agent_greeting = COALESCE($4, agent_greeting),
            agent_language_style = COALESCE($5, agent_language_style)
        WHERE id = $1
        RETURNING agent_name, agent_personality, agent_greeting, agent_language_style
        """,
        business_id,
        agent_name,
        agent_personality,
        agent_greeting,
        agent_language_style,
    )


async def get_brain_snapshot(conn: asyncpg.Connection, business_id: str) -> dict:
    products = await conn.fetch(
        "SELECT * FROM products WHERE business_id = $1 AND is_active = TRUE ORDER BY name",
        business_id,
    )
    services = await conn.fetch(
        "SELECT * FROM services WHERE business_id = $1 AND is_active = TRUE ORDER BY name",
        business_id,
    )
    policy = await conn.fetchrow("SELECT * FROM policies WHERE business_id = $1", business_id)
    permissions = await conn.fetchrow(
        "SELECT * FROM agent_permissions WHERE business_id = $1", business_id
    )
    return {
        "products": [dict(r) for r in products],
        "services": [dict(r) for r in services],
        "policies": dict(policy) if policy else {},
        "permissions": dict(permissions) if permissions else {},
    }


async def upsert_products(conn: asyncpg.Connection, business_id: str, products: list[dict]) -> int:
    count = 0
    for p in products:
        await conn.execute(
            """
            INSERT INTO products (business_id, name, description, price_ngn, stock_count, unit)
            VALUES ($1, $2, $3, $4, $5, COALESCE($6, 'unit'))
            ON CONFLICT (business_id, name) DO UPDATE SET
                description = EXCLUDED.description,
                price_ngn = EXCLUDED.price_ngn,
                stock_count = EXCLUDED.stock_count,
                unit = EXCLUDED.unit,
                updated_at = NOW()
            """,
            business_id,
            p["name"],
            p.get("description"),
            p["price_ngn"],
            p.get("stock_count", 0),
            p.get("unit"),
        )
        count += 1
    return count


async def upsert_services(conn: asyncpg.Connection, business_id: str, services: list[dict]) -> int:
    count = 0
    for s in services:
        await conn.execute(
            """
            INSERT INTO services (business_id, name, description, price_ngn, availability)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (business_id, name) DO UPDATE SET
                description = EXCLUDED.description,
                price_ngn = EXCLUDED.price_ngn,
                availability = EXCLUDED.availability
            """,
            business_id,
            s["name"],
            s.get("description"),
            s["price_ngn"],
            s.get("availability"),
        )
        count += 1
    return count


async def update_policies(conn: asyncpg.Connection, business_id: str, policies: dict) -> bool:
    if not policies:
        return False
    await conn.execute(
        """
        INSERT INTO policies (business_id, delivery, returns, payment_methods, cancellation)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (business_id) DO UPDATE SET
            delivery = COALESCE(EXCLUDED.delivery, policies.delivery),
            returns = COALESCE(EXCLUDED.returns, policies.returns),
            payment_methods = COALESCE(EXCLUDED.payment_methods, policies.payment_methods),
            cancellation = COALESCE(EXCLUDED.cancellation, policies.cancellation)
        """,
        business_id,
        policies.get("delivery"),
        policies.get("returns"),
        policies.get("payment_methods"),
        policies.get("cancellation"),
    )
    return True
