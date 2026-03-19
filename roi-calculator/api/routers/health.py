"""Health check endpoints."""

import time

from fastapi import APIRouter

router = APIRouter(tags=["health"])
START_TIME = time.time()


@router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "uptime_seconds": round(time.time() - START_TIME, 1),
        "version": "0.1.0",
    }
