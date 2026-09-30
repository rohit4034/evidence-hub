from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    queue: Literal["document_ingestion", "embedding", "rerank", "review_generation", "report_export"]
    workspace_id: str
    payload: dict[str, Any] = Field(default_factory=dict)


class JobSummary(BaseModel):
    job_id: str
    queue: str
    status: Literal["queued", "running", "completed", "failed"] = "queued"
    workspace_id: str
