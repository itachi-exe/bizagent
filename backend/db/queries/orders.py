"""Queries against orders and order_line_items."""
import asyncpg


def generate_order_ref(customer_name: str, order_number: int) -> str:
    words = customer_name.strip().split()
    initials = "".join(w[0].upper() for w in words[:2] if w)
    return f"ORD-{initials or 'X'}-{order_number}"


async def list_orders(
    conn: asyncpg.Connection,
    business_id: str,
    status: str | None,
    limit: int,
    offset: int,
) -> list[asyncpg.Record]:
    if status:
        return await conn.fetch(
            """
            SELECT * FROM orders
            WHERE business_id = $1 AND status = $2
            ORDER BY created_at DESC LIMIT $3 OFFSET $4
            """,
            business_id,
            status,
            limit,
            offset,
        )
    return await conn.fetch(
        """
        SELECT * FROM orders
        WHERE business_id = $1
        ORDER BY created_at DESC LIMIT $2 OFFSET $3
        """,
        business_id,
        limit,
        offset,
    )


async def count_orders_today(conn: asyncpg.Connection, business_id: str) -> int:
    row = await conn.fetchrow(
        """
        SELECT COUNT(*) AS n FROM orders
        WHERE business_id = $1 AND created_at >= date_trunc('day', NOW())
        """,
        business_id,
    )
    return row["n"]


async def get_order_by_ref(conn: asyncpg.Connection, business_id: str, order_ref: str) -> asyncpg.Record | None:
    return await conn.fetchrow(
        "SELECT * FROM orders WHERE business_id = $1 AND order_ref = $2",
        business_id,
        order_ref,
    )


async def mark_owner_notified(conn: asyncpg.Connection, order_id: str) -> None:
    await conn.execute("UPDATE orders SET owner_notified_at = NOW() WHERE id = $1", order_id)


async def confirm_delivery(
    conn: asyncpg.Connection,
    order_id: str,
    delivery_info: str,
    delivery_date: str | None,
) -> asyncpg.Record:
    return await conn.fetchrow(
        """
        UPDATE orders SET
            status = 'confirmed',
            delivery_info = $2,
            delivery_date = $3,
            updated_at = NOW()
        WHERE id = $1
        RETURNING *
        """,
        order_id,
        delivery_info,
        delivery_date,
    )


async def list_pending_fulfillment(conn: asyncpg.Connection, business_id: str) -> list[dict]:
    orders = await conn.fetch(
        """
        SELECT o.id AS order_id, o.order_ref, cu.display_name AS customer_name,
               o.total_ngn, o.created_at
        FROM orders o
        JOIN customers cu ON cu.id = o.customer_id
        WHERE o.business_id = $1
          AND o.status = 'pending_payment'
          AND o.owner_notified_at IS NOT NULL
        ORDER BY o.created_at DESC
        """,
        business_id,
    )
    result = []
    for order in orders:
        line_items = await conn.fetch(
            "SELECT product_name, quantity FROM order_line_items WHERE order_id = $1",
            order["order_id"],
        )
        result.append(
            {
                "order_ref": order["order_ref"],
                "customer_name": order["customer_name"],
                "items": [{"product_name": li["product_name"], "quantity": li["quantity"]} for li in line_items],
                "total_ngn": order["total_ngn"],
                "created_at": order["created_at"],
            }
        )
    return result


async def get_line_items(conn: asyncpg.Connection, order_id: str) -> list[asyncpg.Record]:
    return await conn.fetch(
        "SELECT * FROM order_line_items WHERE order_id = $1", order_id
    )
