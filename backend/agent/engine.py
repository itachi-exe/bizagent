"""
STUB ONLY — do not implement real agent logic here.

The real implementation lives in biz-ai-agent.md's scope. This stub exists only
so the backend message pipeline can be exercised end-to-end before that module
is dropped in. Replace this file's body with the real import/implementation —
do not change its signature, callers depend on it.
"""
import asyncio


async def run(conversation_id: str, business_id: str, customer_id: str, message_text: str) -> str:
    await asyncio.sleep(0)  # placeholder for the real (async) agent call
    return (
        "Thanks for your message! (stub agent reply — real agent logic "
        "lives in biz-ai-agent.md and is not implemented here)"
    )


async def notify_customer(order_ref: str, delivery_info: str) -> str:
    """STUB — real implementation composes/sends the delivery-confirmation message to the customer."""
    await asyncio.sleep(0)
    return f"Your order {order_ref} is confirmed for delivery: {delivery_info}"
