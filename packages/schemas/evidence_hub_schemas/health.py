from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    service: str
    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    service: str
    ready: bool
    checks: dict[str, Any] = Field(default_factory=dict)

