import base64
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.manager import manager
from app.services.agent_runner import run_agent
from multi_tool_agent.voice_agent import text_to_speech, speech_to_text

logger = logging.getLogger(__name__)

router = APIRouter()


async def _process_text(websocket: WebSocket, content: str, user_id: str = "default") -> None:
    """Run message through ADK agent, convert to speech, and send back."""
    result = await run_agent(content, user_id=user_id)
    reply = result["content"]
    emotion = result["emotion"]

    audio_b64 = None
    try:
        audio_bytes = text_to_speech(reply)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"TTS failed: {e}")

    response = {
        "type": "response",
        "content": reply,
        "emotion": emotion,
    }
    if audio_b64:
        response["audio_base64"] = audio_b64

    await manager.send_json(websocket, response)


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_type = data.get("type", "text")
            content = data.get("content", "")

            if msg_type == "audio" and content:
                try:
                    audio_bytes = base64.b64decode(content)
                    transcript = speech_to_text(audio_bytes)
                    await manager.send_json(websocket, {"type": "transcript", "content": transcript})
                    await _process_text(websocket, transcript)
                except Exception as e:
                    logger.error(f"STT failed: {e}")
                    await manager.send_json(websocket, {"type": "error", "content": "Failed to transcribe audio."})
            elif msg_type == "text" and content:
                await _process_text(websocket, content)
            else:
                await manager.send_json(websocket, {"type": "error", "content": "Empty or unsupported message"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
