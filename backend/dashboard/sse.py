"""In-process SSE broadcast. Single-process hackathon scale — no Redis pub/sub needed."""
import asyncio
import json
from datetime import datetime, timezone

_subscribers: set[asyncio.Queue] = set()


def subscribe() -> asyncio.Queue:
    queue: asyncio.Queue = asyncio.Queue()
    _subscribers.add(queue)
    return queue


def unsubscribe(queue: asyncio.Queue) -> None:
    _subscribers.discard(queue)


async def broadcast(event_type: str, summary: str, data: dict) -> None:
    event = {
        "type": event_type,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "summary": summary,
        "data": data,
    }
    payload = f"data: {json.dumps(event)}\n\n"
    for queue in list(_subscribers):
        await queue.put(payload)


async def event_stream(queue: asyncio.Queue):
    try:
        while True:
            payload = await queue.get()
            yield payload
    finally:
        unsubscribe(queue)
