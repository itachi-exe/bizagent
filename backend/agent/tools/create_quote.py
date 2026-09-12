from __future__ import annotations

from db.connection import get_pool
from ._shared import as_int, discount_error


async def create_quote(line_items: list[dict], business_id: str, conversation_id: str,
                       discount_pct: int = 0, **_: object) -> dict:
    if not line_items or discount_pct < 0:
        return {"error": "invalid_request", "message": "A quote needs at least one valid item."}
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            perms = await conn.fetchrow("""SELECT can_create_quote, can_approve_discount_up_to_pct
                                            FROM agent_permissions WHERE business_id=$1""", business_id)
            if not perms or not perms["can_create_quote"]:
                return {"error": "permission_denied", "message": "Quote creation requires human approval."}
            permitted = int(perms["can_approve_discount_up_to_pct"])
            if discount_pct > permitted:
                return discount_error(discount_pct, permitted)
            prepared, subtotal = [], 0
            for requested in line_items:
                quantity = requested.get("quantity", 0)
                if not isinstance(quantity, int) or quantity < 1:
                    return {"error": "invalid_request", "message": "Every quote quantity must be at least one."}
                item = await conn.fetchrow("""SELECT id, name, price_ngn FROM products
                                               WHERE id=$1 AND business_id=$2 AND is_active=TRUE""",
                                           requested.get("product_id"), business_id)
                if not item:
                    return {"error": "product_not_found", "message": "One requested product is unavailable."}
                line_total = as_int(item["price_ngn"]) * quantity
                subtotal += line_total
                prepared.append((item, quantity, line_total))
            total = as_int(subtotal * (100 - discount_pct) / 100)
            quote = await conn.fetchrow("""INSERT INTO quotes
                (business_id, conversation_id, subtotal_ngn, discount_pct, total_ngn, expires_at)
                VALUES ($1, $2, $3, $4, $5, NOW() + INTERVAL '7 days')
                RETURNING id, quote_number, total_ngn, expires_at""",
                business_id, conversation_id, subtotal, discount_pct, total)
            for item, quantity, line_total in prepared:
                await conn.execute("""INSERT INTO quote_line_items
                    (quote_id, product_id, product_name, unit_price_ngn, quantity, line_total_ngn)
                    VALUES ($1, $2, $3, $4, $5, $6)""", quote["id"], item["id"], item["name"],
                    as_int(item["price_ngn"]), quantity, line_total)
    return {"quote_id": str(quote["id"]), "quote_number": quote["quote_number"],
            "total_ngn": as_int(quote["total_ngn"]), "expires_at": quote["expires_at"].isoformat(),
            "line_items": [{"product_name": x[0]["name"], "quantity": x[1], "line_total_ngn": x[2]}
                           for x in prepared]}
