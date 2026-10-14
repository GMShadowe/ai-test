import asyncio
import uuid

_pending: dict[str, asyncio.Future] = {}


TOOL = {
    "type": "function",
    "function": {
        "name": "send_message",
        "description": (
            "Send a message to the human operator and wait for their reply. "
            "Use this when you need clarification or want to communicate."
        ),
        "parameters": {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
            "additionalProperties": False,
        },
    },
}


async def execute(text: str, publish_event) -> dict:
    if not text.strip():
        return {"ok": False, "error": "Message is empty"}

    message_id = uuid.uuid4().hex
    future = asyncio.get_running_loop().create_future()
    _pending[message_id] = future

    await publish_event({
        "type": "message",
        "from": "subject",
        "id": message_id,
        "text": text,
    })

    try:
        reply = await asyncio.wait_for(future, timeout=300)
        return {"ok": True, "reply": reply}
    except asyncio.TimeoutError:
        return {"ok": False, "error": "Operator reply timed out"}
    finally:
        _pending.pop(message_id, None)


async def submit_reply(message_id: str, text: str) -> bool:
    future = _pending.get(message_id)
    if future is None or future.done():
        return False

    future.set_result(text)
    return True
