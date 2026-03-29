import base64
import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response
from app.schemas.speech import SpeechRequest, TranscribeRequest
from multi_tool_agent.voice_agent import text_to_speech, speech_to_text

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


@router.post("/transcribe")
async def transcribe(request: TranscribeRequest) -> JSONResponse:
    try:
        audio_bytes = base64.b64decode(request.audio_base64)
        transcript = speech_to_text(audio_bytes, request.language_code)
        return JSONResponse(content={"success": True, "transcript": transcript})
    except Exception as e:
        logger.error(f"Transcribe endpoint error: {e}")
        return JSONResponse(
            status_code=502,
            content={"success": False, "error": "Failed to transcribe audio."},
        )
