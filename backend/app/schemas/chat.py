from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    context: list[dict[str, str]] | None = None


class ChatResponse(BaseModel):
    content: str
    emotion: str
