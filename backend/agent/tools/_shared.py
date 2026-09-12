"""Internal helpers shared by agent tools; never exposed to the model."""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP
from typing import Any

from db.connection import get_pool


def as_int(value: Any) -> int:
    """Convert database numeric values to an integer Naira amount."""
    return int(Decimal(str(value)).quantize(Decimal("1"), rounding=ROUND_HALF_UP))


async def permissions(business_id: str) -> Any:
    pool = get_pool()
    async with pool.acquire() as conn:
        return await conn.fetchrow(
            """SELECT can_create_quote, can_create_order,
                      can_approve_discount_up_to_pct
                 FROM agent_permissions WHERE business_id = $1""",
            business_id,
        )


async def product(product_id: str, business_id: str, conn: Any = None) -> Any:
    sql = """SELECT id, name, price_ngn, stock_count, description, unit
               FROM products
              WHERE id = $1 AND business_id = $2 AND is_active = TRUE"""
    if conn is not None:
        return await conn.fetchrow(sql, product_id, business_id)
    pool = get_pool()
    async with pool.acquire() as acquired:
        return await acquired.fetchrow(sql, product_id, business_id)


def discount_error(requested: int, permitted: int) -> dict[str, Any]:
    return {
        "error": "discount_above_ceiling",
        "requested_pct": requested,
        "max_permitted_pct": permitted,
        "requires_escalation": True,
        "message": "Discount exceeds the approved limit and requires human approval.",
    }
