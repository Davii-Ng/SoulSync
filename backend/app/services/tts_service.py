import io
import logging
from elevenlabs import ElevenLabs
from app.core.config import ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, ELEVENLABS_MODEL_ID

logger = logging.getLogger(__name__)

client = ElevenLabs(api_key=ELEVENLABS_API_KEY)


async def text_to_speech(text: str, voice_id: str | None = None) -> bytes:
    """Convert text to speech using ElevenLabs API. Returns raw audio bytes (mp3)."""
    vid = voice_id or ELEVENLABS_VOICE_ID
    logger.info(f"TTS request: voice={vid}, text_len={len(text)}")

    audio_generator = client.text_to_speech.convert(
        voice_id=vid,
        text=text,
        model_id=ELEVENLABS_MODEL_ID,
        output_format="mp3_44100_128",
    )

    buffer = io.BytesIO()
    for chunk in audio_generator:
        buffer.write(chunk)

    audio_bytes = buffer.getvalue()
    logger.info(f"TTS response: {len(audio_bytes)} bytes")
    return audio_bytes


async def get_available_voices() -> list[dict]:
    """List available ElevenLabs voices."""
    response = client.voices.get_all()
    return [{"voice_id": v.voice_id, "name": v.name} for v in response.voices]
