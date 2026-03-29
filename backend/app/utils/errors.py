from fastapi import Request
from fastapi.responses import JSONResponse


class ServiceError(Exception):
    """Raised when an external service call fails."""

    def __init__(self, service: str, detail: str) -> None:
        self.service = service
        self.detail = detail
        super().__init__(f"{service}: {detail}")


async def service_error_handler(_request: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(
        status_code=502,
        content={"success": False, "error": f"{exc.service} is temporarily unavailable.", "data": None},
    )
