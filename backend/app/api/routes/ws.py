import asyncio
import base64
import json
import logging
from google import genai
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.core.config import GOOGLE_API_KEY
from app.ws.manager import manager
from app.services.agent_runner import run_agent
from multi_tool_agent.voice_agent import text_to_speech, speech_to_text
from multi_tool_agent.core_companion import analyze_emotion, suggest_resource

logger = logging.getLogger(__name__)

router = APIRouter()

_gemini = genai.Client(api_key=GOOGLE_API_KEY)

# Per-connection chat histories keyed by websocket id
_chat_histories: dict[int, list[dict]] = {}

_SYSTEM_PROMPT = (
    "You are SoulSync, a warm and empathetic AI journal companion. "
    "You talk like a caring friend — use contractions, be direct, and keep it real. "
    "Never lecture, never diagnose, never say 'I understand your concerns.' "
    "Reflect their words back naturally, sit with them in it before offering anything. "
    "Keep responses concise (2-4 sentences). "
    "If given emotion context, weave it in naturally — don't announce it."
)


def _build_prompt(content: str, emotion: str, severity: str, suggestion: str, follow_up: str) -> str:
    """Build a Gemini prompt with emotional context."""
    return (
        f"The user said: \"{content}\"\n\n"
        f"Detected emotion: {emotion} (severity: {severity}).\n"
        f"Suggested coping tip: {suggestion}\n"
        f"Suggested follow-up question: {follow_up}\n\n"
        "Using the above context, respond to the user as a caring friend. "
        "Weave in the suggestion or follow-up naturally if appropriate — don't just repeat them verbatim. "
        "Match the emotional intensity. Keep it short and genuine."
    )


async def _generate_reply(ws_id: int, prompt: str) -> str:
    """Call Gemini to generate a contextual response, maintaining conversation history."""
    history = _chat_histories.setdefault(ws_id, [])
    history.append({"role": "user", "parts": [{"text": prompt}]})

    # Keep history bounded to avoid token limits
    trimmed = history[-20:]

    response = await asyncio.to_thread(
        _gemini.models.generate_content,
        model="gemini-3-flash-preview",
        contents=[{"role": "user", "parts": [{"text": _SYSTEM_PROMPT}]}] + trimmed,
    )
    reply = response.text or ""

    history.append({"role": "model", "parts": [{"text": reply}]})
    _chat_histories[ws_id] = history[-20:]
    return reply


async def _process_text(websocket: WebSocket, content: str) -> None:
    """Analyze emotion, generate LLM reply, convert to speech, and send back."""
    try:
        emotion_result = await asyncio.to_thread(analyze_emotion, content)
        emotion = emotion_result.get("emotion", "neutral")
        severity = emotion_result.get("severity", "medium")
        resource_result = await asyncio.to_thread(suggest_resource, emotion, severity)
        suggestion = resource_result.get("suggestion", "")
        follow_up = resource_result.get("follow_up", "")

        prompt = _build_prompt(content, emotion, severity, suggestion, follow_up)
        ws_id = id(websocket)
        reply = await _generate_reply(ws_id, prompt)
    except Exception as e:
        logger.error(f"Agent processing failed: {e}")
        await manager.send_json(websocket, {
            "type": "error",
            "content": "Something went wrong processing your message. Please try again.",
        })
        return

    audio_b64 = None
    try:
        audio_bytes = await asyncio.to_thread(text_to_speech, reply)
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
                    transcript = await asyncio.to_thread(speech_to_text, audio_bytes)
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
        _chat_histories.pop(id(websocket), None)
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        _chat_histories.pop(id(websocket), None)
        manager.disconnect(websocket)
