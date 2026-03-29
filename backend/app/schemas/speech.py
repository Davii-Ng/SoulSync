from pydantic import BaseModel


class SpeechRequest(BaseModel):
    text: str
    voice_id: str | None = None


class TranscribeRequest(BaseModel):
    audio_base64: str
    language_code: str | None = None
