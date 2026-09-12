"""POST /internal/owner-command — handles /deliver commands sent by the business owner.

The Baileys shim routes any message from `owner_phone_number` starting with `/deliver`
here instead of to /internal/message.
"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from agent import engine
from dashboard import sse
from db.connection import get_pool
from db.queries import orders as order_queries
from whatsapp import client as whatsapp_client

logger = logging.getLogger("bizagent.owner_commands")

router = APIRouter()


class OwnerCommandPayload(BaseModel):
    from_: str = Field(alias="from")
    text: str

    model_config = {"populate_by_name": True}


def _parse_deliver_command(text: str) -> tuple[str, str]:
    """'/deliver ORD-KA-1031 Tomorrow 5pm, Swift Courier' -> (order_ref, delivery_info)"""
    parts = text.strip().split(maxsplit=2)
    if len(parts) < 3 or parts[0] != "/deliver":
        raise ValueError("Expected format: /deliver <order_ref> <delivery info>")
    return parts[1], parts[2]


@router.post("/internal/owner-command")
async def handle_owner_command(payload: OwnerCommandPayload):
    try:
        order_ref, delivery_info = _parse_deliver_command(payload.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    pool = get_pool()
    async with pool.acquire() as conn:
        business = await conn.fetchrow("SELECT * FROM businesses LIMIT 1")
        if business is None:
            raise HTTPException(status_code=500, detail="No business configured")

        order = await order_queries.get_order_by_ref(conn, str(business["id"]), order_ref)
        if order is None:
            raise HTTPException(status_code=404, detail=f"No order found with ref {order_ref}")

        updated_order = await order_queries.confirm_delivery(
            conn, str(order["id"]), delivery_info, delivery_date=None
        )
        customer = await conn.fetchrow(
            "SELECT * FROM customers WHERE id = $1", updated_order["customer_id"]
        )

    reply_text = await engine.notify_customer(order_ref, delivery_info)
    await whatsapp_client.send(to=f"{customer['phone_number']}@s.whatsapp.net", text=reply_text)

    await sse.broadcast(
        "order_confirmed",
        f"Order {order_ref} confirmed — customer notified",
        {"order_ref": order_ref, "delivery_info": delivery_info},
    )

    return {"status": "ok"}
