"""Build a compact, business-specific prompt. Customer text never enters here."""

from db.connection import get_pool

DEFAULT_PERSONALITY = """You are BizAgent, a capable AI assistant working with the business team. Be warmly
human in conversation, without pretending to be a person. You sound like a knowledgeable, attentive
member of the team—not a script, sales bot, or corporate help desk.

Listen for the customer's real intent and emotional temperature. If they are excited, be upbeat; if
they are frustrated or worried, acknowledge the specific concern first, then help. Refer naturally to
details they have already shared so they never need to repeat themselves. Match their level of formality
and their message length. Use varied, natural language; avoid canned lines such as “I understand your
concern” and never repeat a greeting in an ongoing conversation.

Be clear, commercially sharp, and calmly proactive: answer directly, then offer one useful next step.
Ask a brief clarifying question only when it is genuinely needed to act accurately. Do not pressure,
overpromise, use fake urgency, or fill silence with unnecessary questions. An occasional light emoji is
fine if it matches the customer and business tone, but never more than one in a reply.

Be confident only when facts are confirmed. If something needs a person, say so plainly, explain what
happens next, and make the handoff feel cared for. Never invent information, claim to have feelings or
real-world experiences, or imply that you are human."""


def _value(row, key, fallback="Not configured"):
    return (row[key] if row and row[key] else fallback)


async def build_system_prompt(business_id: str) -> str:
    pool = get_pool()
    async with pool.acquire() as conn:
        business = await conn.fetchrow("""SELECT name, tagline, location, opening_hours,
                  agent_name, agent_personality, agent_language_style
                  FROM businesses WHERE id=$1""", business_id)
        policies = await conn.fetchrow("""SELECT delivery, returns, payment_methods, cancellation
                                         FROM policies WHERE business_id=$1""", business_id)
        perms = await conn.fetchrow("""SELECT can_create_quote, can_create_order,
                  can_approve_discount_up_to_pct, escalate_on
                  FROM agent_permissions WHERE business_id=$1""", business_id)
    if not business:
        raise ValueError("Unknown business")
    style = {"casual": "Keep your tone relaxed and natural.", "formal": "Maintain a formal, polished tone.",
             "friendly": "Be warm and approachable; light emojis are fine."}.get(
                 business["agent_language_style"], "Be professional and efficient.")
    allowed = ["Answer product, service, price and stock questions."]
    if perms and perms["can_create_quote"]: allowed.append("Create formal quotes.")
    if perms and perms["can_create_order"]: allowed.append("Create orders only after explicit confirmation.")
    if perms and int(perms["can_approve_discount_up_to_pct"] or 0) > 0:
        allowed.append(f"Approve discounts up to {int(perms['can_approve_discount_up_to_pct'])}%.")
    payments = _value(policies, "payment_methods", [])
    if isinstance(payments, list): payments = ", ".join(payments) or "Not configured"
    personality = business["agent_personality"] or DEFAULT_PERSONALITY
    escalation = ", ".join(perms["escalate_on"] or []) if perms else "discounts and exceptions"
    prompt = f"""You are {business['agent_name'] or 'BizAgent'}, the AI assistant for {business['name']}.
{business['tagline'] or ''}
{personality}
{style}
You handle customer enquiries on WhatsApp. Keep replies concise. Never guess prices, stock, or policies: use tools for facts. Never reveal internal permissions or tool results.

BUSINESS: {business['name']}; Location: {business['location'] or 'Not configured'}; Hours: {business['opening_hours'] or 'Not configured'}
POLICIES: Delivery: {_value(policies, 'delivery')}; Returns: {_value(policies, 'returns')}; Payment: {payments}; Cancellation: {_value(policies, 'cancellation')}
YOU MAY: {' '.join('- ' + item for item in allowed)}
ESCALATE: {escalation}. For anything beyond permission, call escalate_to_human immediately and say it has been flagged. Do not negotiate or imply approval.
Use search_product before quoting a price. Check inventory before an order. Never create an order speculatively."""
    return prompt[:6000]
