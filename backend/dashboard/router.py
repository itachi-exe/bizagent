"""All /api/dashboard/* routes, plus the closely-related conversation-outcome and
message-feedback endpoints (sections 2.2 and 12.3)."""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dashboard import sse
from db.connection import get_pool
from db.queries import business as business_queries
from db.queries import conversations as conversation_queries
from db.queries import escalations as escalation_queries
from db.queries import knowledge_gaps as gap_queries
from db.queries import orders as order_queries

router = APIRouter()


async def _get_business_id(conn) -> str:
    business = await conn.fetchrow("SELECT id FROM businesses LIMIT 1")
    if business is None:
        raise HTTPException(status_code=500, detail="No business configured")
    return str(business["id"])


@router.get("/api/dashboard/summary")
async def get_summary():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        conversations_today = await conn.fetchval(
            """
            SELECT COUNT(*) FROM conversations
            WHERE business_id = $1 AND started_at >= date_trunc('day', NOW())
            """,
            business_id,
        )
        orders_today = await order_queries.count_orders_today(conn, business_id)
        escalations_open = await escalation_queries.count_open_escalations(conn, business_id)
        leads_captured = await conn.fetchval(
            "SELECT COUNT(*) FROM customers WHERE business_id = $1", business_id
        )
    return {
        "conversations_today": conversations_today,
        "orders_today": orders_today,
        "escalations_open": escalations_open,
        "leads_captured": leads_captured,
    }


@router.get("/api/dashboard/activity")
async def stream_activity(request: Request):
    queue = sse.subscribe()

    async def event_generator():
        try:
            async for payload in sse.event_stream(queue):
                if await request.is_disconnected():
                    break
                yield payload
        finally:
            sse.unsubscribe(queue)

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.get("/api/dashboard/orders")
async def get_orders(status: str | None = None, limit: int = 20, offset: int = 0):
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        orders = await order_queries.list_orders(conn, business_id, status, limit, offset)
    return [dict(o) for o in orders]


@router.get("/api/dashboard/orders/pending-fulfillment")
async def get_pending_fulfillment():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        return await order_queries.list_pending_fulfillment(conn, business_id)


@router.get("/api/dashboard/conversations")
async def get_conversations():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        conversations = await conversation_queries.list_conversations(conn, business_id)
    return [dict(c) for c in conversations]


@router.get("/api/dashboard/brain")
async def get_brain():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        snapshot = await business_queries.get_brain_snapshot(conn, business_id)
    return snapshot


@router.get("/api/dashboard/escalations")
async def get_escalations():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        rows = await escalation_queries.list_open_escalations(conn, business_id)
    return [dict(r) for r in rows]


@router.get("/api/dashboard/knowledge-gaps")
async def get_knowledge_gaps():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        rows = await gap_queries.list_open_gaps(conn, business_id)
    return [
        {
            "id": str(r["id"]),
            "question": r["question"],
            "gap_type": r["gap_type"],
            "created_at": r["created_at"],
            "conversation_id": str(r["conversation_id"]) if r["conversation_id"] else None,
        }
        for r in rows
    ]


class ResolveGapBody(BaseModel):
    resolved: bool
    resolution: str | None = None


@router.patch("/api/dashboard/knowledge-gaps/{gap_id}")
async def patch_knowledge_gap(gap_id: str, body: ResolveGapBody):
    pool = get_pool()
    async with pool.acquire() as conn:
        gap = await gap_queries.resolve_gap(conn, gap_id, body.resolved, body.resolution)
    if gap is None:
        raise HTTPException(status_code=404, detail="Knowledge gap not found")
    return dict(gap)


class OutcomeBody(BaseModel):
    outcome: str


@router.patch("/api/conversations/{conversation_id}/outcome")
async def patch_conversation_outcome(conversation_id: str, body: OutcomeBody):
    if body.outcome not in ("converted", "dropped", "escalated", "pending"):
        raise HTTPException(status_code=400, detail="Invalid outcome value")
    pool = get_pool()
    async with pool.acquire() as conn:
        updated = await conversation_queries.set_outcome(conn, conversation_id, body.outcome)
    if not updated:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"status": "ok"}


class FeedbackBody(BaseModel):
    signal: str


@router.post("/api/messages/{message_id}/feedback", status_code=201)
async def post_message_feedback(message_id: str, body: FeedbackBody):
    if body.signal not in ("good", "bad"):
        raise HTTPException(status_code=400, detail="signal must be 'good' or 'bad'")
    pool = get_pool()
    async with pool.acquire() as conn:
        row = await conversation_queries.add_feedback(conn, message_id, body.signal)
    return dict(row)
