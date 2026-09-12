"""Typed dataclasses matching the SQL schema. Constructed from asyncpg Record rows."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Business:
    id: UUID
    name: str
    tagline: str | None
    location: str | None
    opening_hours: str | None
    contact_email: str | None
    whatsapp_phone_number: str
    owner_phone_number: str | None
    business_type: str
    agent_name: str
    agent_personality: str | None
    agent_greeting: str | None
    agent_language_style: str
    created_at: datetime


@dataclass
class Product:
    id: UUID
    business_id: UUID
    name: str
    description: str | None
    price_ngn: Decimal
    stock_count: int
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


@dataclass
class Service:
    id: UUID
    business_id: UUID
    name: str
    description: str | None
    price_ngn: Decimal
    availability: str | None
    is_active: bool


@dataclass
class Policy:
    id: UUID
    business_id: UUID
    delivery: str | None
    returns: str | None
    payment_methods: list[str] | None
    cancellation: str | None
    discount_ceiling_pct: int


@dataclass
class AgentPermissions:
    id: UUID
    business_id: UUID
    can_create_order: bool
    can_create_quote: bool
    can_approve_discount_up_to_pct: int
    can_confirm_delivery_date: bool
    escalate_on: list[str]
    negotiation_enabled: bool
    markup_pct: int
    floor_pct: int


@dataclass
class Customer:
    id: UUID
    business_id: UUID
    phone_number: str
    display_name: str | None
    first_seen_at: datetime
    last_seen_at: datetime


@dataclass
class Conversation:
    id: UUID
    business_id: UUID
    customer_id: UUID
    started_at: datetime
    last_message_at: datetime
    status: str
    outcome: str | None
    outcome_set_at: datetime | None


@dataclass
class Message:
    id: UUID
    conversation_id: UUID
    wamid: str | None
    role: str
    content: str
    sent_at: datetime


@dataclass
class Order:
    id: UUID
    order_number: int
    order_ref: str | None
    business_id: UUID
    customer_id: UUID
    conversation_id: UUID | None
    status: str
    total_ngn: Decimal
    discount_pct: int
    notes: str | None
    delivery_info: str | None
    delivery_date: str | None
    owner_notified_at: datetime | None
    created_by: str
    created_at: datetime
    updated_at: datetime


@dataclass
class OrderLineItem:
    id: UUID
    order_id: UUID
    product_id: UUID | None
    product_name: str
    unit_price_ngn: Decimal
    quantity: int
    line_total_ngn: Decimal


@dataclass
class Escalation:
    id: UUID
    business_id: UUID
    conversation_id: UUID | None
    reason: str
    customer_message: str | None
    summary: str | None
    created_at: datetime
    resolved_at: datetime | None
    resolved_by: str | None


@dataclass
class CustomerMemory:
    id: UUID
    business_id: UUID
    customer_id: UUID
    memory: str
    created_at: datetime
    created_by: str


@dataclass
class KnowledgeGap:
    id: UUID
    business_id: UUID
    conversation_id: UUID | None
    question: str
    gap_type: str
    resolved: bool
    resolution: str | None
    created_at: datetime
    resolved_at: datetime | None
