from fastapi import APIRouter
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/")
async def health_check() -> APIResponse:
    return APIResponse(
        success=True,
        data={"status": "healthy", "service": "SoulSync", "version": "0.1.0"},
    )
