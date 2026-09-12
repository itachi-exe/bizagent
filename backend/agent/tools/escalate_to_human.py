from __future__ import annotations

from db.connection import get_pool

VALID_REASONS = {"discount_above_ceiling", "refund_request", "complaint", "out_of_scope", "customer_request"}


async def escalate_to_human(reason: str, summary: str, business_id: str,
                            conversation_id: str, **_: object) -> dict:
    if reason not in VALID_REASONS:
        return {"error": "invalid_request", "message": "A valid escalation reason is required."}
    pool = get_pool()
    async with pool.acquire() as conn:
        async with conn.transaction():
            escalation_id = await conn.fetchval("""INSERT INTO escalations
                (business_id, conversation_id, reason, summary)
                VALUES ($1, $2, $3, $4) RETURNING id""",
                business_id, conversation_id, reason, summary[:1000])
            await conn.execute("UPDATE conversations SET status='escalated' WHERE id=$1 AND business_id=$2",
                               conversation_id, business_id)
    return {"escalation_id": str(escalation_id), "status": "flagged",
            "message": "Escalation logged. The team has been notified."}
