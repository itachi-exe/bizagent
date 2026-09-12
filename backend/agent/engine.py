"""Stateless OpenAI tool loop: the backend calls ``await run(...)``."""

from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any

from openai import AsyncOpenAI

from db.connection import get_pool
from .context import load_history
from .prompt import build_system_prompt
from .tool_registry import TOOL_SCHEMAS
from .tools import TOOL_HANDLERS

logger = logging.getLogger(__name__)
FALLBACK_REPLY = "I'm having some trouble with that. Please try again or speak to a team member."
MAX_TOOL_CALLS = 5


def _valid(value: Any, schema: dict) -> bool:
    kind = schema.get("type")
    if kind == "string": return isinstance(value, str) and (value in schema["enum"] if "enum" in schema else True)
    if kind == "integer": return isinstance(value, int) and not isinstance(value, bool) and value >= schema.get("minimum", float("-inf"))
    if kind == "array": return isinstance(value, list) and len(value) >= schema.get("minItems", 0) and all(_valid(x, schema["items"]) for x in value)
    if kind == "object":
        return isinstance(value, dict) and all(key in value for key in schema.get("required", [])) and all(
            key in schema.get("properties", {}) and _valid(item, schema["properties"][key]) for key, item in value.items())
    return False


SCHEMAS = {entry["function"]["name"]: entry["function"]["parameters"] for entry in TOOL_SCHEMAS}


async def _audit(conversation_id: str, business_id: str, name: str, arguments: dict, result: dict) -> None:
    try:
        pool = get_pool()
        async with pool.acquire() as conn:
            await conn.execute("""INSERT INTO tool_calls (tool_name, arguments, result)
                                  VALUES ($1, $2::jsonb, $3::jsonb)""",
                               name, json.dumps(arguments), json.dumps(result))
    except Exception:
        logger.exception("Could not audit tool call")


async def _execute(call: Any, conversation_id: str, business_id: str) -> tuple[Any, dict]:
    try:
        arguments = json.loads(call.function.arguments)
        handler = TOOL_HANDLERS.get(call.function.name)
        if not handler or not _valid(arguments, SCHEMAS.get(call.function.name, {})):
            result = {"error": "invalid_tool_arguments", "message": "The request could not be processed."}
        else:
            result = await handler(**arguments, conversation_id=conversation_id, business_id=business_id)
    except (json.JSONDecodeError, TypeError, ValueError):
        result = {"error": "invalid_tool_arguments", "message": "The request could not be processed."}
    except Exception:
        logger.exception("Tool %s failed", call.function.name)
        result = {"error": "tool_unavailable", "message": "That action is temporarily unavailable."}
        arguments = {}
    await _audit(conversation_id, business_id, call.function.name, arguments, result)
    return call, result


async def _persist_agent_message(conversation_id: str, content: str) -> None:
    pool = get_pool()
    async with pool.acquire() as conn:
        await conn.execute("INSERT INTO messages (conversation_id, role, content) VALUES ($1, 'agent', $2)",
                           conversation_id, content)


async def run(conversation_id: str, business_id: str, message_text: str) -> str:
    """Return the final customer-facing reply; transport delivery stays with the backend."""
    try:
        system, history = await asyncio.gather(build_system_prompt(business_id), load_history(conversation_id))
        messages: list[dict] = [{"role": "system", "content": system}, *history]
        # Production adapters commonly save the inbound message before invoking us.
        # Avoid showing that exact current message twice while still supporting callers
        # that invoke the engine before persistence.
        if not history or history[-1] != {"role": "user", "content": message_text}:
            messages.append({"role": "user", "content": message_text})
        client = AsyncOpenAI(
            api_key=os.environ.get("OPENAI_API_KEY"),
            base_url=os.environ.get("OPENAI_BASE_URL", "https://api.deepseek.com/v1"),
        )
        tool_count = 0
        while tool_count < MAX_TOOL_CALLS:
            response = await client.chat.completions.create(
                model=os.environ.get("OPENAI_MODEL", "gpt-4o"), messages=messages,
                tools=TOOL_SCHEMAS, tool_choice="auto", temperature=0.2)
            choice = response.choices[0].message
            if not choice.tool_calls:
                reply = (choice.content or "").strip() or FALLBACK_REPLY
                await _persist_agent_message(conversation_id, reply)
                return reply
            remaining = MAX_TOOL_CALLS - tool_count
            calls = list(choice.tool_calls)[:remaining]
            messages.append(choice.model_dump(exclude_none=True))
            completed = await asyncio.gather(*(_execute(call, conversation_id, business_id) for call in calls))
            for call, result in completed:
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result)})
            tool_count += len(calls)
    except Exception:
        logger.exception("Agent run failed")
    await _persist_agent_message(conversation_id, FALLBACK_REPLY)
    return FALLBACK_REPLY
