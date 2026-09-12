from __future__ import annotations

from db.connection import get_pool
from ._shared import as_int, discount_error


async def create_order(line_items: list[dict], business_id: str, conversation_id: str,
                       discount_pct: int = 0, notes: str = "", **_: object) -> dict:
    if not line_items or discount_pct < 0:
        return {"error": "invalid_request", "message": "An order needs at least one valid item."}
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            perms = await conn.fetchrow("""SELECT can_create_order, can_approve_discount_up_to_pct
                                            FROM agent_permissions WHERE business_id=$1""", business_id)
            if not perms or not perms["can_create_order"]:
                return {"error": "permission_denied", "message": "Order creation requires human approval for this business."}
            permitted = int(perms["can_approve_discount_up_to_pct"])
            if discount_pct > permitted:
                return discount_error(discount_pct, permitted)

            requested: dict[str, int] = {}
            for line in line_items:
                product_id, quantity = line.get("product_id"), line.get("quantity", 0)
                if not product_id or not isinstance(quantity, int) or quantity < 1:
                    return {"error": "invalid_request", "message": "Every order quantity must be at least one."}
                requested[product_id] = requested.get(product_id, 0) + quantity

            prepared, subtotal = [], 0
            for product_id, quantity in requested.items():
                item = await conn.fetchrow("""SELECT id, name, price_ngn, stock_count FROM products
                    WHERE id=$1 AND business_id=$2 AND is_active=TRUE FOR UPDATE""", product_id, business_id)
                if not item:
                    return {"error": "product_not_found", "message": "One requested product is unavailable."}
                if item["stock_count"] < quantity:
                    return {"error": "insufficient_stock", "product_name": item["name"],
                            "requested": quantity, "available": item["stock_count"]}
                line_total = as_int(item["price_ngn"]) * quantity
                subtotal += line_total
                prepared.append((item, quantity, line_total))

            total = as_int(subtotal * (100 - discount_pct) / 100)
            order = await conn.fetchrow("""INSERT INTO orders
                (business_id, conversation_id, status, subtotal_ngn, discount_pct, total_ngn, notes)
                VALUES ($1, $2, 'pending_payment', $3, $4, $5, $6)
                RETURNING id, order_number, status, total_ngn, created_at""",
                business_id, conversation_id, subtotal, discount_pct, total, notes[:1000])
            for item, quantity, line_total in prepared:
                await conn.execute("""INSERT INTO order_line_items
                    (order_id, product_id, product_name, unit_price_ngn, quantity, line_total_ngn)
                    VALUES ($1, $2, $3, $4, $5, $6)""", order["id"], item["id"], item["name"],
                    as_int(item["price_ngn"]), quantity, line_total)
                await conn.execute("UPDATE products SET stock_count=stock_count-$1 WHERE id=$2", quantity, item["id"])
    return {"order_id": str(order["id"]), "order_number": order["order_number"], "status": order["status"],
            "total_ngn": as_int(order["total_ngn"]), "created_at": order["created_at"].isoformat(),
            "line_items": [{"product_name": x[0]["name"], "quantity": x[1], "line_total_ngn": x[2]}
                           for x in prepared]}
