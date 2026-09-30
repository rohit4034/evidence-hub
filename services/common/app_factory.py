from __future__ import annotations

from collections.abc import Callable
from typing import Any, Optional

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from evidence_hub_schemas.health import HealthResponse, ReadinessResponse
from services.common.settings import ServiceSettings, get_settings


def create_service_app(
    title: str,
    *,
    description: str,
    configure: Optional[Callable[[FastAPI, ServiceSettings], None]] = None,
) -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=title, description=description, version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    router = APIRouter()

    @router.get("/health", response_model=HealthResponse, tags=["system"])
    def health() -> HealthResponse:
        return HealthResponse(service=settings.service_name, status="ok")

    @router.get("/ready", response_model=ReadinessResponse, tags=["system"])
    def ready() -> ReadinessResponse:
        checks: dict[str, Any] = {
            "settings": "ok",
            "postgres_url_configured": bool(settings.postgres_url),
            "redis_url_configured": bool(settings.redis_url),
        }
        return ReadinessResponse(service=settings.service_name, ready=True, checks=checks)

    app.include_router(router)

    if configure is not None:
        configure(app, settings)

    return app

