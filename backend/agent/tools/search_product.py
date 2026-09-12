from __future__ import annotations

from db.connection import get_pool
from ._shared import as_int


async def search_product(query: str, business_id: str, **_: object) -> dict:
    query = query.strip()
    if not query:
        return {"found": False, "message": "No products matched that search."}
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch(
            """SELECT id, name, price_ngn, stock_count, description, unit
                 FROM products
                WHERE business_id = $1 AND is_active = TRUE
                  AND (name ILIKE '%' || $2 || '%' OR description ILIKE '%' || $2 || '%')
                ORDER BY similarity(name, $2) DESC
                LIMIT 5""",
            business_id, query,
        )
    if not rows:
        return {"found": False, "message": f"No products matched '{query}'."}
    return {"found": True, "results": [
        {"id": str(row["id"]), "name": row["name"], "price_ngn": as_int(row["price_ngn"]),
         "stock_count": row["stock_count"], "unit": row["unit"],
         "description": row["description"] or ""}
        for row in rows
    ]}
