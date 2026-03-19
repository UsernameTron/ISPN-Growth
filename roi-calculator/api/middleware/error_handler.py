"""Error handling middleware."""

import logging

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception as exc:
            logger.exception("Unhandled error during request %s %s", request.method, request.url.path)
            return JSONResponse(
                status_code=500,
                content={"success": False, "error": str(exc), "detail": "Internal server error"},
            )
