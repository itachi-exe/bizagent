-- BizAgent Seed Data — Macaney Demo
-- Run after schema.sql against the same database.

DO $$
DECLARE
    v_business_id UUID;
BEGIN
    INSERT INTO businesses (
        name, tagline, location, opening_hours, whatsapp_phone_number,
        owner_phone_number, business_type,
        agent_name, agent_personality, agent_greeting, agent_language_style
    )
    VALUES (
        'Macaney Sustainable Solutions',
        'Ethical beekeeping products and training in Abuja',
        'Abuja, Nigeria',
        'Monday–Friday 8am–6pm, Saturday 9am–2pm',
        '2348012345678',
        '2348012345678',
        'retail',
        'Zara',
        'Warm and knowledgeable about beekeeping. You speak to customers like a helpful friend who happens to know everything about bees. You use light emojis occasionally. You always greet customers by name if you have it.',
        'Hi there! 🐝 I''m Zara, your assistant at Macaney Sustainable Solutions. How can I help you today?',
        'friendly'
    )
    RETURNING id INTO v_business_id;

    INSERT INTO products (business_id, name, description, price_ngn, stock_count, unit)
    VALUES
        (v_business_id, 'Langstroth Beehive', 'Standard 10-frame Langstroth hive, complete kit', 35000, 42, 'unit'),
        (v_business_id, 'Protective Suit', 'Full-body beekeeper suit with veil, sizes S–XL', 18000, 28, 'unit'),
        (v_business_id, 'Bee Smoker', 'Stainless steel bellows smoker with heat shield', 8500, 60, 'unit'),
        (v_business_id, 'Bee Feed (5kg)', 'Supplemental sugar syrup feed for colonies', 4500, 120, 'bag');

    INSERT INTO services (business_id, name, description, price_ngn, availability)
    VALUES
        (v_business_id, 'Beginner Beekeeping Training', '1-day hands-on introduction to beekeeping', 25000, 'First Saturday of each month'),
        (v_business_id, 'Advanced Colony Management', '2-day advanced course for practicing beekeepers', 45000, 'By arrangement');

    INSERT INTO policies (business_id, delivery, returns, payment_methods, cancellation, discount_ceiling_pct)
    VALUES (
        v_business_id,
        'Delivery within Abuja: NGN 2,000 flat. Outside Abuja: calculated per order. Allow 2–5 business days.',
        'Unused items in original packaging returnable within 7 days.',
        ARRAY['Bank transfer', 'Paystack', 'Cash on delivery (Abuja only)'],
        'Orders cancelled before dispatch: full refund. After dispatch: no cancellation.',
        10
    );

    INSERT INTO agent_permissions (
        business_id, can_create_order, can_create_quote, can_approve_discount_up_to_pct,
        can_confirm_delivery_date, escalate_on, negotiation_enabled, markup_pct, floor_pct
    )
    VALUES (
        v_business_id, TRUE, TRUE, 0, FALSE,
        ARRAY['discount_above_ceiling', 'refund_request', 'complaint'],
        FALSE, 0, 0
    );
END $$;
