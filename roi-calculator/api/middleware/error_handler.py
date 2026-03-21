"""Error handling middleware with consistent error response envelope."""

import logging
from typing import Any

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)


def error_response(
    status_code: int,
    error: str,
    message: str,
    *,
    detail: Any = None,
    request_id: str | None = None,
) -> JSONResponse:
    """Build a consistent error response envelope."""
    body: dict[str, Any] = {
        "success": False,
        "error": error,
        "message": message,
    }
    if detail is not None:
        body["detail"] = detail
    if request_id is not None:
        body["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=body)


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled error during request %s %s", request.method, request.url.path)
            request_id = getattr(request.state, "request_id", None)
            return error_response(
                500,
                "internal_server_error",
                "Internal server error",
                request_id=request_id,
            )
