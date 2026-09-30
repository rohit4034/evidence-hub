from __future__ import annotations

from uuid import uuid5, NAMESPACE_URL

from fastapi import APIRouter, FastAPI

from evidence_hub_schemas.jobs import JobCreate, JobSummary
from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings

JOBS: dict[str, JobSummary] = {}


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:12]}"


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(prefix="/jobs", tags=["jobs"])

    @router.get("/queues")
    def queues() -> dict[str, list[str]]:
        return {
            "queues": ["document_ingestion", "embedding", "rerank", "review_generation", "report_export"],
            "phase1_status": ["queue_contracts", "job_enqueue", "artifact_volume_contracts"],
        }

    @router.post("", response_model=JobSummary)
    def enqueue(payload: JobCreate) -> JobSummary:
        job_id = _stable_id("job", f"{payload.workspace_id}:{payload.queue}:{payload.payload}")
        job = JobSummary(job_id=job_id, queue=payload.queue, workspace_id=payload.workspace_id)
        JOBS[job_id] = job
        return job

    @router.get("", response_model=list[JobSummary])
    def list_jobs() -> list[JobSummary]:
        return list(JOBS.values())

    app.include_router(router)


app = create_service_app(
    "Evidence Hub Worker Service",
    description="Background job boundary for ingestion, indexing, AI traces, and exports.",
    configure=configure,
)
