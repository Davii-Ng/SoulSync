import logging
from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.schemas.common import APIResponse
from app.services.agent_runner import run_agent

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest) -> APIResponse:
    try:
        result = await run_agent(request.message)
        return APIResponse(
            success=True,
            data=ChatResponse(
                content=result["content"],
                emotion=result["emotion"],
            ).model_dump(),
        )
    except Exception as e:
        logger.error(f"Chat endpoint error: {e}")
        return APIResponse(success=False, error="Failed to generate response. Please try again.")
