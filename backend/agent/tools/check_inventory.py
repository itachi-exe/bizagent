from __future__ import annotations

from ._shared import product


async def check_inventory(product_id: str, business_id: str, **_: object) -> dict:
    item = await product(product_id, business_id)
    if not item:
        return {"error": "product_not_found", "message": "That product is unavailable."}
    count = item["stock_count"]
    result = {"product_id": str(item["id"]), "product_name": item["name"],
              "stock_count": count, "can_fulfill": count > 0}
    if count <= 0:
        result["message"] = "This product is currently out of stock."
    return result
