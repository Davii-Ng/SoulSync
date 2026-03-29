import logging
from fastapi import FastAPI
from app.core.config import LOG_LEVEL, APP_ENV
from app.core.security import configure_cors
from app.utils.errors import ServiceError, service_error_handler
from app.api.routes import health, chat, speech, ws

logging.basicConfig(level=getattr(logging, LOG_LEVEL), format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(title="SoulSync API", version="0.1.0")

configure_cors(app)
app.add_exception_handler(ServiceError, service_error_handler)  # type: ignore[arg-type]

app.include_router(health.router)
app.include_router(chat.router)
app.include_router(speech.router)
app.include_router(ws.router)

logger.info(f"SoulSync backend started (env={APP_ENV})")