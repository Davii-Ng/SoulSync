import io
import os
import logging

from dotenv import load_dotenv
from elevenlabs import ElevenLabs
from google.adk.agents.llm_agent import Agent

load_dotenv()

logger = logging.getLogger(__name__)

_api_key = os.getenv("ELEVENLABS_API_KEY")
_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "JBFqnCBsd6RMkjVDRZzb")
_model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")

_client = ElevenLabs(api_key=_api_key) if _api_key else None


def speak_response(response_text: str) -> dict:
    """Converts response text to audio via ElevenLabs TTS.

    Args:
        response_text: The text to convert to speech audio.

    Returns:
        dict with status and base64-encoded mp3 audio bytes.
    """
    if not _client:
        return {"status": "error", "message": "ELEVENLABS_API_KEY not set."}

    try:
        audio_generator = _client.text_to_speech.convert(
            voice_id=_voice_id,
            text=response_text,
            model_id=_model_id,
            output_format="mp3_44100_128",
        )

        buffer = io.BytesIO()
        for chunk in audio_generator:
            buffer.write(chunk)

        audio_bytes = buffer.getvalue()
        logger.info(f"TTS response: {len(audio_bytes)} bytes")
        return {"status": "success", "audio_bytes": len(audio_bytes)}
    except Exception as e:
        logger.error(f"ElevenLabs TTS failed: {e}")
        return {"status": "error", "message": str(e)}


def text_to_speech(text: str, voice_id: str | None = None) -> bytes:
    """Backend-facing TTS helper. Returns raw mp3 bytes for API routes."""
    if not _client:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    vid = voice_id or _voice_id
    audio_generator = _client.text_to_speech.convert(
        voice_id=vid,
        text=text,
        model_id=_model_id,
        output_format="mp3_44100_128",
    )

    buffer = io.BytesIO()
    for chunk in audio_generator:
        buffer.write(chunk)
    return buffer.getvalue()


def speech_to_text(audio_bytes: bytes, language_code: str | None = None) -> str:
    """Backend-facing STT helper. Returns transcript text from raw audio bytes."""
    if not _client:
        raise RuntimeError("ELEVENLABS_API_KEY not set")

    response = _client.speech_to_text.convert(
        model_id="scribe_v1",
        file=audio_bytes,
        language_code=language_code,
    )
    return response.text


async def get_available_voices() -> list[dict]:
    """List available ElevenLabs voices with gender labels."""
    if not _client:
        raise RuntimeError("ELEVENLABS_API_KEY not set")
    response = _client.voices.get_all()
    voices = []
    for v in response.voices:
        gender = (v.labels or {}).get("gender", "unknown") if hasattr(v, "labels") else "unknown"
        voices.append({"voice_id": v.voice_id, "name": v.name, "gender": gender})
    return voices


voice_agent = Agent(
    model="gemini-3.1-pro-preview",
    name="voice_agent",
    description="Converts text responses to natural-sounding audio via ElevenLabs TTS.",
    instruction=(
        "You are SoulSync's Voice Agent. Your sole responsibility is to convert text into audio. "
        "Use 'speak_response' with the final response text and return the audio output. "
        "Do not modify or interpret the text — only convert it to speech."
    ),
    tools=[speak_response],
)
