"""httpx client for sending outbound WhatsApp messages via the Baileys shim."""
import logging
import os

import httpx

logger = logging.getLogger("bizagent.whatsapp")

_client: httpx.AsyncClient | None = None


def get_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(timeout=10.0)
    return _client


async def send(to: str, text: str) -> bool:
    """POST to the Baileys shim /send endpoint. Never raises — logs and returns False on failure."""
    shim_url = os.environ["BAILEYS_SHIM_URL"]
    try:
        client = get_client()
        response = await client.post(f"{shim_url}/send", json={"to": to, "text": text})
        response.raise_for_status()
        return True
    except httpx.HTTPError:
        logger.exception("Failed to reach Baileys shim at %s while sending to %s", shim_url, to)
        return False


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
