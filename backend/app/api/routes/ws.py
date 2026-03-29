import base64
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.ws.manager import manager
from multi_tool_agent.core_companion import analyze_emotion, suggest_resource
from multi_tool_agent.voice_agent import text_to_speech

logger = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            msg_type = data.get("type", "text")
            content = data.get("content", "")

            if msg_type == "text" and content:
                # Analyze emotion and get coping suggestion
                emotion_result = analyze_emotion(content)
                emotion = emotion_result.get("emotion", "neutral")
                resource_result = suggest_resource(emotion)
                reply = resource_result.get("suggestion", "")

                # Generate TTS audio
                audio_b64 = None
                try:
                    audio_bytes = await text_to_speech(reply)
                    audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
                except Exception as e:
                    logger.error(f"TTS failed: {e}")

                # Send response matching frontend's expected format
                response = {
                    "type": "response",
                    "content": reply,
                    "emotion": emotion,
                }
                if audio_b64:
                    response["audio_base64"] = audio_b64

                await manager.send_json(websocket, response)
            else:
                await manager.send_json(websocket, {"type": "error", "content": "Empty or unsupported message"})

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
