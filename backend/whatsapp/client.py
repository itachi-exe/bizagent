"""httpx client for sending outbound WhatsApp messages via the Baileys shim."""
import asyncio
import logging
import os
import subprocess
import tempfile
from pathlib import Path

import httpx

logger = logging.getLogger("bizagent.whatsapp")

_client: httpx.AsyncClient | None = None

VOICE_REPLIES = os.environ.get("VOICE_REPLIES", "false").lower() == "true"
TTS_SCRIPT = "/opt/hermes/.hermes/scripts/tts.py"


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=10.0)
    return _client


async def send(to: str, text: str) -> bool:
    """POST to the Baileys shim /send endpoint. Never raises — logs and returns False on failure."""
    shim_url = os.environ.get("BAILEYS_SHIM_URL", "http://localhost:8002")
    try:
        client = get_client()
        response = await client.post(f"{shim_url}/send", json={"to": to, "text": text})
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Failed to reach Baileys shim at %s while sending to %s", shim_url, to)
        return False


async def send_voice(to: str, text: str) -> bool:
    """Generate a Kokoro TTS voice note and send it as a WhatsApp PTT audio message."""
    shim_url = os.environ.get("BAILEYS_SHIM_URL", "http://localhost:8002")
    ogg_path = tempfile.mktemp(suffix=".ogg", dir="/tmp")
    try:
        loop = asyncio.get_event_loop()
        proc = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                ["python3", TTS_SCRIPT, text, ogg_path],
                capture_output=True,
                timeout=30,
            ),
        )
        if proc.returncode != 0:
            logger.error("TTS failed: %s", proc.stderr.decode())
            return False

        client = get_client()
        response = await client.post(
            f"{shim_url}/send-voice",
            json={"to": to, "audio_path": ogg_path},
        )
        response.raise_for_status()
        logger.info("[VOICE QUEUED] to=%s", to)
        return True
    except Exception:
        logger.exception("send_voice failed for %s", to)
        return False
    finally:
        Path(ogg_path).unlink(missing_ok=True)


def _format_line_items(line_items) -> str:
    return ", ".join(f"{li['quantity']}x {li['product_name']}" for li in line_items)


async def notify_owner_new_order(order, customer, business, line_items) -> None:
    """Called after create_order succeeds (by the agent's order-creation tool)."""
    message = (
        f"New order via BizAgent:\n"
        f"Order {order['order_ref']}\n"
        f"Customer: {customer['display_name']} (+{customer['phone_number']})\n"
        f"Items: {_format_line_items(line_items)}\n"
        f"Total: NGN {order['total_ngn']:,.0f}\n\n"
        f"Reply with delivery details:\n"
        f"/deliver {order['order_ref']} [date] [notes]"
    )
    if business["owner_phone_number"]:
        await send(to=f"{business['owner_phone_number']}@s.whatsapp.net", text=message)
