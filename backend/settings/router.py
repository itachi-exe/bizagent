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


@router.get("/api/settings/business")
async def get_business_settings():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        settings = await conn.fetchrow(
            """
            SELECT name, tagline, location, opening_hours, contact_email,
                   whatsapp_phone_number, owner_phone_number, business_type,
                   agent_name, agent_personality, agent_greeting, agent_language_style
            FROM businesses WHERE id = $1
            """,
            business_id,
        )
    return dict(settings)


class BusinessSettingsUpdate(BaseModel):
    name: str | None = None
    tagline: str | None = None
    location: str | None = None
    opening_hours: str | None = None
    contact_email: str | None = None
    whatsapp_phone_number: str | None = None
    owner_phone_number: str | None = None
    business_type: str | None = None


@router.patch("/api/settings/business")
async def patch_business_settings(body: BusinessSettingsUpdate):
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        updated = await conn.fetchrow(
            """
            UPDATE businesses SET
                name = COALESCE($2, name),
                tagline = COALESCE($3, tagline),
                location = COALESCE($4, location),
                opening_hours = COALESCE($5, opening_hours),
                contact_email = COALESCE($6, contact_email),
                whatsapp_phone_number = COALESCE($7, whatsapp_phone_number),
                owner_phone_number = COALESCE($8, owner_phone_number),
                business_type = COALESCE($9, business_type)
            WHERE id = $1
            RETURNING name, tagline, location, opening_hours, contact_email,
                      whatsapp_phone_number, owner_phone_number, business_type,
                      agent_name, agent_personality, agent_greeting, agent_language_style
            """,
            business_id,
            body.name,
            body.tagline,
            body.location,
            body.opening_hours,
            body.contact_email,
            body.whatsapp_phone_number,
            body.owner_phone_number,
            body.business_type,
        )
    return dict(updated)


@router.get("/api/settings/policies")
async def get_policies_settings():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        settings = await conn.fetchrow(
            "SELECT * FROM policies WHERE business_id = $1", business_id
        )
    return dict(settings)


class PoliciesSettingsUpdate(BaseModel):
    delivery: str | None = None
    returns: str | None = None
    payment_methods: list[str] | None = None
    cancellation: str | None = None
    discount_ceiling_pct: int | None = None


@router.patch("/api/settings/policies")
async def patch_policies_settings(body: PoliciesSettingsUpdate):
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        updated = await conn.fetchrow(
            """
            UPDATE policies SET
                delivery = COALESCE($2, delivery),
                returns = COALESCE($3, returns),
                payment_methods = COALESCE($4, payment_methods),
                cancellation = COALESCE($5, cancellation),
                discount_ceiling_pct = COALESCE($6, discount_ceiling_pct)
            WHERE business_id = $1
            RETURNING *
            """,
            business_id,
            body.delivery,
            body.returns,
            body.payment_methods,
            body.cancellation,
            body.discount_ceiling_pct,
        )
    return dict(updated)


@router.get("/api/settings/permissions")
async def get_permissions_settings():
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        settings = await conn.fetchrow(
            "SELECT * FROM agent_permissions WHERE business_id = $1", business_id
        )
    return dict(settings)


class PermissionsSettingsUpdate(BaseModel):
    can_create_order: bool | None = None
    can_create_quote: bool | None = None
    can_approve_discount_up_to_pct: int | None = None
    can_confirm_delivery_date: bool | None = None
    escalate_on: list[str] | None = None
    negotiation_enabled: bool | None = None
    markup_pct: int | None = None
    floor_pct: int | None = None


@router.patch("/api/settings/permissions")
async def patch_permissions_settings(body: PermissionsSettingsUpdate):
    pool = get_pool()
    async with pool.acquire() as conn:
        business_id = await _get_business_id(conn)
        updated = await conn.fetchrow(
            """
            UPDATE agent_permissions SET
                can_create_order = COALESCE($2, can_create_order),
                can_create_quote = COALESCE($3, can_create_quote),
                can_approve_discount_up_to_pct = COALESCE($4, can_approve_discount_up_to_pct),
                can_confirm_delivery_date = COALESCE($5, can_confirm_delivery_date),
                escalate_on = COALESCE($6, escalate_on),
                negotiation_enabled = COALESCE($7, negotiation_enabled),
                markup_pct = COALESCE($8, markup_pct),
                floor_pct = COALESCE($9, floor_pct)
            WHERE business_id = $1
            RETURNING *
            """,
            business_id,
            body.can_create_order,
            body.can_create_quote,
            body.can_approve_discount_up_to_pct,
            body.can_confirm_delivery_date,
            body.escalate_on,
            body.negotiation_enabled,
            body.markup_pct,
            body.floor_pct,
        )
    return dict(updated)
