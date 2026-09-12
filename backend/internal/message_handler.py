"""POST /internal/message — receives normalized messages from the Baileys shim.

Bound to localhost only (enforced by main.py binding, not here). Flow:
validate → dedup → upsert customer → get/create conversation → persist message →
dispatch to agent engine in a BackgroundTask → return 200 immediately.
"""
import logging

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agent import engine
from dashboard import sse
from db.connection import get_pool
from db.queries import conversations as conversation_queries
from db.queries import customers as customer_queries
from whatsapp import client as whatsapp_client

logger = logging.getLogger("bizagent.message_handler")

router = APIRouter()


class IncomingMessagePayload(BaseModel):
    message_id: str
    phone_number: str
    display_name: str | None = None
    text: str
    timestamp: int


@router.post("/internal/message")
async def receive_message(payload: IncomingMessagePayload, background_tasks: BackgroundTasks):
    if not payload.phone_number or not payload.text or not payload.message_id:
        raise HTTPException(status_code=400, detail="phone_number, text, and message_id are required")

    pool = get_pool()
    async with pool.acquire() as conn:
        if await conversation_queries.message_exists(conn, payload.message_id):
            return {"status": "duplicate_ignored"}

        # Hackathon MVP: single seeded business. Multi-business routing is out of scope.
        business = await conn.fetchrow("SELECT * FROM businesses LIMIT 1")
        if business is None:
            raise HTTPException(status_code=500, detail="No business configured")
        business_id = str(business["id"])

        customer = await customer_queries.get_or_create_customer(
            conn, business_id, payload.phone_number, payload.display_name
        )
        conversation = await conversation_queries.get_or_create_active_conversation(
            conn, business_id, str(customer["id"])
        )
        await conversation_queries.insert_message(
            conn, str(conversation["id"]), payload.message_id, "customer", payload.text
        )
        await conversation_queries.touch_conversation(conn, str(conversation["id"]))

    await sse.broadcast(
        "message_received",
        f"New message from {customer['display_name'] or customer['phone_number']}",
        {"conversation_id": str(conversation["id"]), "text": payload.text},
    )

    background_tasks.add_task(
        _dispatch_to_agent,
        str(conversation["id"]),
        business_id,
        str(customer["id"]),
        payload.text,
        payload.phone_number,
    )

    return {"status": "accepted"}


async def _dispatch_to_agent(
    conversation_id: str,
    business_id: str,
    customer_id: str,
    message_text: str,
    to_phone_number: str,
) -> None:
    """Runs in the background after the HTTP response has already been sent."""
    pool = get_pool()
    try:
        # engine.run() persists the agent message itself — no double-insert here
        reply_text = await engine.run(conversation_id, business_id, message_text)
    except Exception:
        logger.exception("Agent engine raised for conversation %s", conversation_id)
        reply_text = "I'm having trouble right now. Please try again in a moment."
        async with pool.acquire() as conn:
            await conversation_queries.insert_message(conn, conversation_id, None, "agent", reply_text)

    async with pool.acquire() as conn:
        await conversation_queries.touch_conversation(conn, conversation_id)

    sent = await whatsapp_client.send(to=f"{to_phone_number}@s.whatsapp.net", text=reply_text)
    if not sent:
        logger.error("Could not deliver reply for conversation %s — Baileys shim unreachable", conversation_id)

    if whatsapp_client.VOICE_REPLIES and reply_text:
        await whatsapp_client.send_voice(to=f"{to_phone_number}@s.whatsapp.net", text=reply_text)
