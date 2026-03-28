# Backend Entry Point

# FastAPI app with WebSocket endpoint for real-time frontend communication.
# This is the API layer only — all AI logic lives in agents/.

# Endpoints:
#   GET  /   — health check
#   WS   /ws — main WebSocket for voice/text communication

# Run: cd backend && uvicorn main:app --reload


import json
import uuid
import logging
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(dotenv_path="../.env")

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("soulsync")

# FastAPI app
app = FastAPI(title="SoulSync API", version="0.1.0")

# CORS — allow frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store (hackathon scope)
# { session_id: { "history": [...], "created_at": "..." } }
sessions: dict[str, dict] = {}


def get_or_create_session(session_id: str | None) -> str:
    """Return existing session_id or create a new one."""
    if session_id and session_id in sessions:
        return session_id

    new_id = session_id or str(uuid.uuid4())
    sessions[new_id] = {
        "history": [],
        "created_at": datetime.now().isoformat(),
    }
    logger.info(f"New session created: {new_id}")
    return new_id


async def process_message(text: str, session_id: str) -> dict:
    """
    Process user message through agents and return response.

    TODO: Replace mock with real agent calls when Davie finishes core_companion.
      from agents.core_companion import process
      result = await process(text, sessions[session_id])
    """
    # Store user message in session history
    sessions[session_id]["history"].append({
        "role": "user",
        "text": text,
        "timestamp": datetime.now().isoformat(),
    })

    # MOCK RESPONSE (swap with real agent later) 
    response_text = f"I hear you. You said: \"{text}\". I'm here for you."
    emotion = "neutral"
    # END MOCK

    # Store AI response in session history
    sessions[session_id]["history"].append({
        "role": "assistant",
        "text": response_text,
        "emotion": emotion,
        "timestamp": datetime.now().isoformat(),
    })

    return {
        "type": "response",
        "text": response_text,
        "emotion": emotion,
        "audio_url": None,  # TODO: ElevenLabs TTS via voice_agent
        "session_id": session_id,
    }


# Endpoints

@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "soulsync-backend",
        "version": "0.1.0",
        "active_sessions": len(sessions),
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Main WebSocket endpoint for real-time communication with frontend.

    Expected incoming JSON:
      { "type": "message", "text": "...", "session_id": "..." }

    Outgoing JSON:
      { "type": "response", "text": "...", "emotion": "...", "audio_url": null, "session_id": "..." }
    """
    await websocket.accept()
    session_id: str | None = None
    logger.info("WebSocket connection opened")

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON",
                })
                continue

            msg_type = data.get("type")

            if msg_type == "message":
                text = data.get("text", "").strip()
                if not text:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Empty message",
                    })
                    continue

                # Get or create session
                session_id = get_or_create_session(
                    data.get("session_id") or session_id
                )

                # Process through agents (mock for now)
                response = await process_message(text, session_id)
                await websocket.send_json(response)

            elif msg_type == "ping":
                await websocket.send_json({"type": "pong"})

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Unknown message type: {msg_type}",
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected (session: {session_id})")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await websocket.close(code=1011, reason=str(e))