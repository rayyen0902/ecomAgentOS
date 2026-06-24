"""FastAPI application entry point."""

import time

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.v1.health import router as health_router
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger

settings = get_settings()
configure_logging(level=settings.log_level, fmt=settings.log_format)
logger = get_logger()
logger.info(
    "application_startup",
    app_name=settings.app_name,
    app_version=settings.app_version,
    app_env=settings.app_env,
    log_format=settings.log_format,
)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log every incoming request with method, path, status_code, duration_ms, request_id."""

    async def dispatch(self, request: Request, call_next):
        start = time.perf_counter()
        response = await call_next(request)
        duration_ms = int((time.perf_counter() - start) * 1000)
        request_id = request.headers.get(
            "X-Request-ID",
            getattr(request.state, "request_id", ""),
        )
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
            request_id=request_id,
        )
        return response


app = FastAPI(
    title=get_settings().app_name,
    version=get_settings().app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(RequestLoggingMiddleware)
app.include_router(health_router, prefix="/api/v1")
