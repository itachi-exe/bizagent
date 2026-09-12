from __future__ import annotations

from ._shared import as_int, discount_error, permissions, product


async def calculate_price(product_id: str, quantity: int, business_id: str,
                          discount_pct: int = 0, **_: object) -> dict:
    if quantity < 1 or discount_pct < 0:
        return {"error": "invalid_request", "message": "Quantity and discount must be valid."}
    item, perms = await product(product_id, business_id), await permissions(business_id)
    if not item:
        return {"error": "product_not_found", "message": "That product is unavailable."}
    permitted = int(perms["can_approve_discount_up_to_pct"]) if perms else 0
    if discount_pct > permitted:
        return discount_error(discount_pct, permitted)
    unit_price = as_int(item["price_ngn"])
    subtotal = unit_price * quantity
    total = as_int(subtotal * (100 - discount_pct) / 100)
    return {"product_name": item["name"], "unit_price_ngn": unit_price, "quantity": quantity,
            "discount_pct": discount_pct, "subtotal_ngn": subtotal, "total_ngn": total}
