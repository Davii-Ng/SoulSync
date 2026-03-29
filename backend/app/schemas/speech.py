from pydantic import BaseModel


class SpeechRequest(BaseModel):
    text: str
    voice_id: str | None = None
