"""GET + PATCH /api/settings/bot — agent customization (section 5.3)."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from db.connection import get_pool
from db.queries import business as business_queries

router = APIRouter()

VALID_LANGUAGE_STYLES = {"professional", "friendly", "casual", "formal"}


async def _get_business_id(conn) -> str:
    business = await conn.fetchrow("SELECT id FROM businesses LIMIT 1")
    if business is None:
        raise HTTPException(status_code=500, detail="No business configured")
    return str(business["id"])


@router.get("/api/settings/bot")
async def get_bot_settings():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        settings = await business_queries.get_bot_settings(conn, business_id)
    return dict(settings)


class BotSettingsUpdate(BaseModel):
    agent_name: str | None = Field(default=None, max_length=40)
    agent_personality: str | None = Field(default=None, max_length=500)
    agent_greeting: str | None = Field(default=None, max_length=300)
    agent_language_style: str | None = None


@router.patch("/api/settings/bot")
async def patch_bot_settings(body: BotSettingsUpdate):
    if body.agent_language_style is not None and body.agent_language_style not in VALID_LANGUAGE_STYLES:
        raise HTTPException(
            status_code=400,
            detail=f"agent_language_style must be one of {sorted(VALID_LANGUAGE_STYLES)}",
        )

    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        updated = await business_queries.update_bot_settings(
            conn,
            business_id,
            body.agent_name,
            body.agent_personality,
            body.agent_greeting,
            body.agent_language_style,
        )
    return dict(updated)
