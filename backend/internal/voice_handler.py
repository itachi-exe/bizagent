"""POST /internal/voice-message — receives voice notes from the Baileys shim.

Flow: audio_path → Whisper transcription → same pipeline as text message.
"""
import asyncio
import logging
import subprocess
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel

from agent import engine
from dashboard import sse
from db.connection import get_pool
from db.queries import conversations as conversation_queries
from db.queries import customers as customer_queries
from whatsapp import client as whatsapp_client

logger = logging.getLogger("bizagent.voice_handler")
router = APIRouter()


class VoiceMessagePayload(BaseModel):
    message_id: str
    phone_number: str
    display_name: str | None = None
    audio_path: str
    timestamp: int


async def transcribe(audio_path: str) -> str:
    """Run Whisper in an executor so it doesn't block the event loop."""
    loop = asyncio.get_event_loop()

    def _run():
        result = subprocess.run(
            ["python3", "-c",
             f"import whisper, os; m=whisper.load_model('base'); r=m.transcribe('{audio_path}'); print(r['text'].strip())"],
            capture_output=True, text=True, timeout=60
        )
        return result.stdout.strip()

    text = await loop.run_in_executor(None, _run)
    Path(audio_path).unlink(missing_ok=True)
    return text or ""


@router.post("/internal/voice-message")
async def receive_voice_message(payload: VoiceMessagePayload, background_tasks: BackgroundTasks):
    if not payload.phone_number or not payload.audio_path or not payload.message_id:
        raise HTTPException(status_code=400, detail="phone_number, audio_path, and message_id are required")

    pool = get_pool()
    async with pool.acquire() as conn:
        if await conversation_queries.message_exists(conn, payload.message_id):
            return {"status": "duplicate_ignored"}

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

    await sse.broadcast(
        "voice_received",
        f"Voice note from {customer['display_name'] or customer['phone_number']}",
        {"conversation_id": str(conversation["id"])},
    )

    background_tasks.add_task(
        _dispatch_voice,
        payload.audio_path,
        str(conversation["id"]),
        business_id,
        payload.message_id,
        payload.phone_number,
    )

    return {"status": "accepted"}


async def _dispatch_voice(
    audio_path: str,
    conversation_id: str,
    business_id: str,
    message_id: str,
    to_phone_number: str,
) -> None:
    pool = get_pool()

    # Transcribe
    text = await transcribe(audio_path)
    if not text:
        logger.warning("Whisper returned empty transcript for %s", audio_path)
        text = "Sorry, I couldn't understand that voice note. Could you type your message?"
        await whatsapp_client.send_voice(to=f"{to_phone_number}@s.whatsapp.net", text=text)
        return

    logger.info("[VOICE TRANSCRIPT] %s → %s", to_phone_number, text)

    async with pool.acquire() as conn:
        await conversation_queries.insert_message(conn, conversation_id, message_id, "customer", f"[Voice] {text}")
        await conversation_queries.touch_conversation(conn, conversation_id)

    try:
        reply_text = await engine.run(conversation_id, business_id, text)
    except Exception:
        logger.exception("Agent engine raised for conversation %s", conversation_id)
        reply_text = "I'm having trouble right now. Please try again in a moment."
        async with pool.acquire() as conn:
            await conversation_queries.insert_message(conn, conversation_id, None, "agent", reply_text)

    async with pool.acquire() as conn:
        await conversation_queries.touch_conversation(conn, conversation_id)

    # Always reply with voice for voice messages
    await whatsapp_client.send_voice(to=f"{to_phone_number}@s.whatsapp.net", text=reply_text)
