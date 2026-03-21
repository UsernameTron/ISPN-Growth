"""ISPN ROI Calculator — FastAPI application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from api.config import settings
from api.middleware.error_handler import ErrorHandlerMiddleware, error_response
from api.middleware.logging_middleware import LoggingMiddleware
from api.routers import calculate, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


def create_app() -> FastAPI:
    app = FastAPI(
        title="ISPN ROI Calculator API",
        version="0.1.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(LoggingMiddleware)
    app.add_middleware(ErrorHandlerMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", None)
        return error_response(
            422,
            "validation_error",
            "Validation error",
            detail=exc.errors(),
            request_id=request_id,
        )

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", None)
        return error_response(
            500,
            "internal_server_error",
            "Internal server error",
            request_id=request_id,
        )

    app.include_router(health.router, prefix="/api")
    app.include_router(calculate.router, prefix="/api")

    return app


app = create_app()
