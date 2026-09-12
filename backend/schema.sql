-- BizAgent Backend — Full Database Schema
-- Run once against a fresh PostgreSQL 15 database.
-- gen_random_uuid() is built into PostgreSQL 13+ core; no extension needed.

-- ============================================================
-- Businesses
-- ============================================================
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    tagline TEXT,
    location TEXT,
    opening_hours TEXT,
    contact_email TEXT,
    whatsapp_phone_number TEXT NOT NULL,
    owner_phone_number TEXT,
    business_type TEXT NOT NULL DEFAULT 'retail',
    agent_name TEXT NOT NULL DEFAULT 'Assistant',
    agent_personality TEXT,
    agent_greeting TEXT,
    agent_language_style TEXT NOT NULL DEFAULT 'professional',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Products
-- ============================================================
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    price_ngn NUMERIC(12, 2) NOT NULL,
    stock_count INT NOT NULL DEFAULT 0,
    unit TEXT NOT NULL DEFAULT 'unit',
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(business_id, name)
);
CREATE INDEX idx_products_business ON products(business_id) WHERE is_active = TRUE;

-- ============================================================
-- Services
-- ============================================================
CREATE TABLE services (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    description TEXT,
    price_ngn NUMERIC(12, 2) NOT NULL,
    availability TEXT,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE(business_id, name)
);

-- ============================================================
-- Policies (one row per business)
-- ============================================================
CREATE TABLE policies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE UNIQUE,
    delivery TEXT,
    returns TEXT,
    payment_methods TEXT[],
    cancellation TEXT,
    discount_ceiling_pct INT NOT NULL DEFAULT 0
);

-- ============================================================
-- Agent permissions (one row per business)
-- ============================================================
CREATE TABLE agent_permissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE UNIQUE,
    can_create_order BOOLEAN NOT NULL DEFAULT FALSE,
    can_create_quote BOOLEAN NOT NULL DEFAULT TRUE,
    can_approve_discount_up_to_pct INT NOT NULL DEFAULT 0,
    can_confirm_delivery_date BOOLEAN NOT NULL DEFAULT FALSE,
    escalate_on TEXT[] NOT NULL DEFAULT '{discount_above_ceiling,refund_request,complaint}',
    negotiation_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    markup_pct INT NOT NULL DEFAULT 0,
    floor_pct INT NOT NULL DEFAULT 0
);

-- ============================================================
-- Customers
-- ============================================================
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    phone_number TEXT NOT NULL,
    display_name TEXT,
    first_seen_at TIMESTAMPTZ DEFAULT NOW(),
    last_seen_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(business_id, phone_number)
);

-- ============================================================
-- Conversations
-- ============================================================
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active',  -- active | escalated | closed
    outcome TEXT,                            -- converted | dropped | escalated | pending
    outcome_set_at TIMESTAMPTZ
);
CREATE INDEX idx_conversations_customer ON conversations(customer_id);
CREATE INDEX idx_conversations_business ON conversations(business_id, status);

-- ============================================================
-- Messages
-- ============================================================
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    wamid TEXT UNIQUE,                       -- Baileys message_id, for dedup
    role TEXT NOT NULL,                      -- customer | agent | system
    content TEXT NOT NULL,
    sent_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, sent_at);

-- ============================================================
-- Tool call audit trail
-- ============================================================
CREATE TABLE tool_calls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    tool_name TEXT NOT NULL,
    arguments JSONB NOT NULL,
    result JSONB NOT NULL,
    called_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Orders
-- ============================================================
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_number SERIAL,
    order_ref TEXT UNIQUE,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id),
    conversation_id UUID REFERENCES conversations(id),
    status TEXT NOT NULL DEFAULT 'pending_payment',
    total_ngn NUMERIC(12, 2) NOT NULL,
    discount_pct INT NOT NULL DEFAULT 0,
    notes TEXT,
    delivery_info TEXT,
    delivery_date TEXT,
    owner_notified_at TIMESTAMPTZ,
    created_by TEXT NOT NULL DEFAULT 'agent',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Order line items
-- ============================================================
CREATE TABLE order_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name TEXT NOT NULL,
    unit_price_ngn NUMERIC(12, 2) NOT NULL,
    quantity INT NOT NULL,
    line_total_ngn NUMERIC(12, 2) NOT NULL
);

-- ============================================================
-- Quotes
-- ============================================================
CREATE TABLE quotes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_number SERIAL,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id),
    conversation_id UUID REFERENCES conversations(id),
    total_ngn NUMERIC(12, 2) NOT NULL,
    discount_pct INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours',
    converted_to_order_id UUID REFERENCES orders(id)
);

-- ============================================================
-- Quote line items
-- ============================================================
CREATE TABLE quote_line_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    quote_id UUID REFERENCES quotes(id) ON DELETE CASCADE,
    product_id UUID REFERENCES products(id),
    product_name TEXT NOT NULL,
    unit_price_ngn NUMERIC(12, 2) NOT NULL,
    quantity INT NOT NULL,
    line_total_ngn NUMERIC(12, 2) NOT NULL
);

-- ============================================================
-- Escalations
-- ============================================================
CREATE TABLE escalations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),
    reason TEXT NOT NULL,
    customer_message TEXT,
    summary TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    resolved_by TEXT
);

-- ============================================================
-- Uploads (Business Brain population)
-- ============================================================
CREATE TABLE uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    extracted_data JSONB NOT NULL,   -- the preview shown to owner
    confirmed_at TIMESTAMPTZ,        -- null until owner confirms
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Persistent customer memory
-- ============================================================
CREATE TABLE customer_memories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    customer_id UUID REFERENCES customers(id) ON DELETE CASCADE,
    memory TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    created_by TEXT NOT NULL DEFAULT 'agent',   -- agent | human
    UNIQUE(customer_id, memory)
);
CREATE INDEX idx_memories_customer ON customer_memories(customer_id);

-- ============================================================
-- Knowledge gaps
-- ============================================================
CREATE TABLE knowledge_gaps (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id),
    question TEXT NOT NULL,
    gap_type TEXT NOT NULL,          -- product_not_found | policy_missing | out_of_scope
    resolved BOOLEAN NOT NULL DEFAULT FALSE,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ
);

-- ============================================================
-- Message feedback
-- ============================================================
CREATE TABLE message_feedback (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES messages(id) ON DELETE CASCADE,
    signal TEXT NOT NULL,            -- good | bad
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- Extended business brain (per business_type)
-- ============================================================
CREATE TABLE business_brain_extended (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE UNIQUE,
    term_dates TEXT,
    admission_requirements TEXT,
    fee_structure JSONB,
    departments TEXT[],
    consultation_fee_ngn NUMERIC(12,2),
    appointment_lead_time TEXT,
    event_packages JSONB,
    venue_capacity INT,
    menu JSONB,
    delivery_zones TEXT[],
    listing_count INT,
    property_types TEXT[],
    route_pricing JSONB,
    max_weight_kg INT
);
