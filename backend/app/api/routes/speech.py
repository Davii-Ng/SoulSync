import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from app.schemas.speech import SpeechRequest
from multi_tool_agent.voice_agent import text_to_speech

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/speech")
async def speech(request: SpeechRequest) -> Response:
    try:
        audio_bytes = text_to_speech(request.text, request.voice_id)
        return Response(
            content=audio_bytes,
            media_type="audio/mpeg",
            headers={
                "Content-Length": str(len(audio_bytes)),
                "Accept-Ranges": "bytes",
            },
        )
    except Exception as e:
        logger.error(f"Speech endpoint error: {e}")
        return JSONResponse(
            status_code=502,
            content={"success": False, "error": "Failed to generate speech audio."},
        )
