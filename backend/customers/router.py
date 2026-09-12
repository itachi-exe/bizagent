"""Customer memory endpoints (section 11.3).

Memories are written by the agent's remember_customer tool directly — there is
no write endpoint here, only read and owner-initiated delete.
"""
from fastapi import APIRouter, HTTPException

from db.connection import get_pool
from db.queries import customers as customer_queries

router = APIRouter()


@router.get("/api/customers/{customer_id}/memories")
async def get_customer_memories(customer_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        rows = await customer_queries.get_memories(conn, customer_id)
    return [
        {"id": str(r["id"]), "memory": r["memory"], "created_at": r["created_at"], "created_by": r["created_by"]}
        for r in rows
    ]


@router.delete("/api/customers/{customer_id}/memories/{memory_id}", status_code=204)
async def delete_customer_memory(customer_id: str, memory_id: str):
    pool = get_pool()
    async with pool.acquire() as conn:
        deleted = await customer_queries.delete_memory(conn, customer_id, memory_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Memory not found")
    return None
