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

logger = logging.getLogger(__name__)

router = APIRouter()

# Per-connection voice preference (websocket id → voice_id)
_voice_prefs: dict[int, str] = {}

# Retained for prompt reference. The active response path uses ADK via run_agent().
_SYSTEM_PROMPT = (
    "You are SoulSync, a warm and empathetic AI journal companion. "
    "You talk like a caring friend, use contractions, be direct, and keep it real. "
    "Never lecture, never diagnose, never say 'I understand your concerns.' "
    "Reflect their words back naturally, sit with them in it before offering anything. "
    "Keep responses concise (2-4 sentences). "
    "If given emotion context, weave it in naturally and do not announce it."
)

# Legacy direct-Gemini support (currently unused; ADK run_agent is active path).
_gemini = genai.Client(api_key=GOOGLE_API_KEY)
_chat_histories: dict[int, list[dict]] = {}


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


async def _process_text(websocket: WebSocket, content: str, voice_id: str | None = None) -> None:
    """Run ADK pipeline, convert response to speech, and send back."""
    try:
        user_id = str(id(websocket))
        agent_result = await run_agent(content, user_id=user_id)
        reply = (agent_result.get("content") or "").strip()
        emotion = agent_result.get("emotion", "neutral")
        events = agent_result.get("events", [])
        if not reply:
            reply = "I'm here with you. Want to share a little more about what's on your mind?"
    except Exception as e:
        logger.error(f"Agent processing failed: {e}")
        await manager.send_json(websocket, {
            "type": "error",
            "content": "Something went wrong processing your message. Please try again.",
        })
        return

    audio_b64 = None
    tts_error = None
    try:
        audio_bytes = await asyncio.to_thread(text_to_speech, reply, voice_id)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
    except Exception as e:
        logger.error(f"TTS failed: {e}")
        tts_error = "Voice unavailable — ElevenLabs quota exceeded." if "quota" in str(e).lower() else "Voice temporarily unavailable."

    response = {
        "type": "response",
        "content": reply,
        "emotion": emotion,
    }
    if events:
        response["events"] = events
    if tts_error:
        response["tts_error"] = tts_error
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

            ws_id = id(websocket)

            # Store voice preference per connection
            if msg_type == "set_voice":
                vid = data.get("voice_id", "")
                if vid:
                    _voice_prefs[ws_id] = vid
                else:
                    _voice_prefs.pop(ws_id, None)
                await manager.send_json(websocket, {"type": "voice_set", "voice_id": vid or None})
                continue

            # Resolve voice: per-message override > per-connection pref > server default
            voice_id = data.get("voice_id") or _voice_prefs.get(ws_id)

            if msg_type == "audio" and content:
                try:
                    audio_bytes = base64.b64decode(content)
                    transcript = await asyncio.to_thread(speech_to_text, audio_bytes)
                    await manager.send_json(websocket, {"type": "transcript", "content": transcript})
                    await _process_text(websocket, transcript, voice_id)
                except Exception as e:
                    logger.error(f"STT failed: {e}")
                    await manager.send_json(websocket, {"type": "error", "content": "Failed to transcribe audio."})
            elif msg_type == "text" and content:
                await _process_text(websocket, content, voice_id)
            else:
                await manager.send_json(websocket, {"type": "error", "content": "Empty or unsupported message"})

    except WebSocketDisconnect:
        _voice_prefs.pop(id(websocket), None)
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        _voice_prefs.pop(id(websocket), None)
        manager.disconnect(websocket)
