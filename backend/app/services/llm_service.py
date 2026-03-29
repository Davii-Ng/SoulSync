import json
import logging
from google import genai
from google.genai import types
from app.core.config import GOOGLE_API_KEY

logger = logging.getLogger(__name__)

_client = genai.Client(api_key=GOOGLE_API_KEY)
_MODEL = "gemini-3-flash-preview"

SYSTEM_PROMPT = """You are SoulSync, an empathetic AI mental health companion. You help people dealing with burnout, stress, and loneliness.

Rules:
- Be warm, validating, and non-judgmental
- Keep responses concise (2-4 sentences) since they will be spoken aloud
- Detect the user's emotional state from their message
- If someone is in crisis, gently suggest professional resources (988 Suicide & Crisis Lifeline, therapist, etc.)
- Never diagnose conditions or prescribe medication
- You are a supportive companion, not a replacement for professional help

You MUST respond with valid JSON in this exact format:
{"content": "your empathetic response here", "emotion": "one of: calm, stressed, anxious, happy, sad, angry, neutral"}
"""


async def generate_response(message: str, context: list[dict[str, str]] | None = None) -> dict:
    """Generate an empathetic response with emotion detection using Gemini API."""
    try:
        return await _gemini_response(message, context)
    except Exception as e:
        logger.error(f"Gemini API call failed: {e}")
        return _fallback_response(message)


async def _gemini_response(message: str, context: list[dict[str, str]] | None = None) -> dict:
    """Call Gemini API for response generation."""
    contents: list[types.Content] = []
    if context:
        for msg in context:
            role = "model" if msg.get("role") == "assistant" else "user"
            text = msg.get("content") or msg.get("message") or msg.get("text", "")
            if text:
                contents.append(types.Content(role=role, parts=[types.Part(text=text)]))

    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))

    response = await _client.aio.models.generate_content(
        model=_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
        ),
    )

    text = response.text.strip() if response.text else ""
    if not text:
        return {"content": "I'm here for you. Could you tell me more about how you're feeling?", "emotion": "neutral"}

    try:
        result = json.loads(text)
        content = result.get("content") or result.get("response") or result.get("text") or text
        emotion = result.get("emotion", "neutral")
        return {"content": content, "emotion": emotion}
    except (json.JSONDecodeError, ValueError):
        logger.warning(f"Failed to parse Gemini JSON response, raw: {text}")
        return {"content": text, "emotion": "neutral"}


def _fallback_response(message: str) -> dict:
    """Simple fallback when Gemini API call fails."""
    lower = message.lower()
    if any(w in lower for w in ["stress", "overwhelm", "pressure", "burnout"]):
        return {
            "content": "It sounds like you're carrying a heavy load right now. That takes real strength to acknowledge. What's weighing on you the most?",
            "emotion": "stressed",
        }
    if any(w in lower for w in ["sad", "lonely", "alone", "miss", "cry", "depressed"]):
        return {
            "content": "I hear you, and those feelings are completely valid. You don't have to go through this alone. I'm here to listen.",
            "emotion": "sad",
        }
    if any(w in lower for w in ["anxious", "worry", "scared", "panic", "nervous", "concerned"]):
        return {
            "content": "Anxiety can feel so overwhelming. Let's take a breath together. Can you tell me what's on your mind right now?",
            "emotion": "anxious",
        }
    if any(w in lower for w in ["angry", "mad", "frustrated", "furious"]):
        return {
            "content": "It's okay to feel angry. That emotion is telling you something important. What happened that brought this up?",
            "emotion": "angry",
        }
    if any(w in lower for w in ["happy", "great", "good", "amazing", "excited"]):
        return {
            "content": "That's wonderful to hear! I'm glad you're feeling good. What's bringing you joy today?",
            "emotion": "happy",
        }
    return {
        "content": "Thank you for sharing that with me. I'm here to listen and support you. How are you feeling right now?",
        "emotion": "neutral",
    }
