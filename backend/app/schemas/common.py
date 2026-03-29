from typing import Any
from pydantic import BaseModel
import uuid


class APIResponse(BaseModel):
    success: bool
    data: Any = None
    error: str | None = None
    request_id: str = ""

    def __init__(self, **kwargs: Any) -> None:
        if "request_id" not in kwargs or not kwargs["request_id"]:
            kwargs["request_id"] = str(uuid.uuid4())
        super().__init__(**kwargs)
