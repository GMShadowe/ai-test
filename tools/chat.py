import asyncio

_pending_replies: dict[str, asyncio.Future] = {}
_reply_counter = 0
_reply_lock = asyncio.Lock()


async def send_message(text: str, publish_event) -> dict:
    global _reply_counter

    if not text.strip():
        return {"ok": False, "error": "Message is empty"}

    async with _reply_lock:
        _reply_counter += 1
        message_id = str(_reply_counter)
        future = asyncio.get_running_loop().create_future()
        _pending_replies[message_id] = future

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
        _pending_replies.pop(message_id, None)


async def submit_reply(message_id: str, text: str) -> bool:
    future = _pending_replies.get(message_id)

    if future is None or future.done():
        return False

    future.set_result(text)
    return True
