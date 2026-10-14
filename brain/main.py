import asyncio
import os
import time
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from brain.brain import run_agent
from tools.chat import submit_reply

load_dotenv()

clients: set[WebSocket] = set()
operator_queue: asyncio.Queue = asyncio.Queue()
agent_task: asyncio.Task | None = None
started_at: float | None = None
status = "idle"


async def publish_event(event: dict):
    event.setdefault("time", time.time())
    disconnected = []

    for client in list(clients):
        try:
            await client.send_json(event)
        except Exception:
            disconnected.append(client)

    for client in disconnected:
        clients.discard(client)


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if agent_task and not agent_task.done():
        agent_task.cancel()
        try:
            await agent_task
        except asyncio.CancelledError:
            pass


app = FastAPI(title="AI Containment Lab", lifespan=lifespan)

# Restrict this list to your dashboard's actual origin before exposing
# the API on a network. This default is for local UI development only.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


class StartRequest(BaseModel):
    prompt: str = Field(min_length=1, max_length=4000)


class ChatRequest(BaseModel):
    text: str = Field(min_length=1, max_length=4000)


class ReplyRequest(BaseModel):
    message_id: str
    text: str = Field(min_length=1, max_length=4000)


@app.get("/api/status")
async def get_status():
    return {
        "status": status,
        "uptime": int(time.time() - started_at) if started_at else 0,
        "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    }


@app.post("/api/start")
async def start_experiment(request: StartRequest):
    global agent_task, started_at, status

    if not os.getenv("GROQ_API_KEY"):
        raise HTTPException(500, "GROQ_API_KEY is not configured")

    if agent_task and not agent_task.done():
        raise HTTPException(409, "Experiment is already running")

    while not operator_queue.empty():
        operator_queue.get_nowait()

    started_at = time.time()
    status = "running"

    await publish_event({
        "type": "log",
        "tag": "SYS",
        "text": "Experiment started",
    })

    agent_task = asyncio.create_task(
        run_agent(request.prompt, publish_event, operator_queue)
    )

    return {"ok": True, "status": status}


@app.post("/api/stop")
async def stop_experiment():
    global agent_task, status

    if agent_task and not agent_task.done():
        agent_task.cancel()
        try:
            await agent_task
        except asyncio.CancelledError:
            pass

    status = "stopped"
    await publish_event({
        "type": "status",
        "status": status,
    })
    return {"ok": True, "status": status}


@app.post("/api/chat")
async def operator_message(request: ChatRequest):
    await operator_queue.put(request.text)
    await publish_event({
        "type": "message",
        "from": "operator",
        "text": request.text,
    })
    return {"ok": True}


@app.post("/api/reply")
async def operator_reply(request: ReplyRequest):
    accepted = await submit_reply(request.message_id, request.text)
    if not accepted:
        raise HTTPException(404, "No active request is waiting for this reply")
    await publish_event({
        "type": "message",
        "from": "operator",
        "text": request.text,
        "reply_to": request.message_id,
    })
    return {"ok": True}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.add(websocket)

    try:
        await websocket.send_json({
            "type": "status",
            "status": status,
            "model": os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        })

        while True:
            # Keep the connection alive. Dashboard commands use HTTP.
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    finally:
        clients.discard(websocket)
