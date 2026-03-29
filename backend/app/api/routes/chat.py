import logging
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import APIResponse
from multi_tool_agent.core_companion import analyze_emotion, suggest_resource

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest) -> APIResponse:
    try:
        emotion_result = analyze_emotion(request.message)
        emotion = emotion_result.get("emotion", "neutral")
        resource_result = suggest_resource(emotion)
        return APIResponse(
            success=True,
            data=ChatResponse(
                content=resource_result.get("suggestion", ""),
                emotion=emotion,
            ).model_dump(),
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return APIResponse(success=False, error="Failed to generate response. Please try again.")
