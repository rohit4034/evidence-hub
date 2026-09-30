from __future__ import annotations

from fastapi import APIRouter, FastAPI

from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(tags=["gateway"])

    @router.get("/services")
    def service_directory() -> dict[str, object]:
        return {
            "ai_service_url": settings.ai_service_url,
            "evidence_service_url": settings.evidence_service_url,
            "compliance_service_url": settings.compliance_service_url,
            "support_service_url": settings.support_service_url,
            "worker_service_url": settings.worker_service_url,
        }

    @router.get("/phase1")
    def phase1_manifest() -> dict[str, object]:
        return {
            "status": "ready_for_github_backed_dokploy_setup",
            "runtime_target": "Dokploy via GitHub repository",
            "modules": ["Evidence Desk", "Compliance Desk", "Support Triage", "AI Service", "Worker Service"],
            "guardrails": [
                "NVIDIA_API_KEY is read from env only",
                "product services call the internal AI service instead of NVIDIA directly",
                "AI route metadata is admin-safe and redacted",
                "customer data defaults to private and requires opt-in for eval or training use",
                "citations are validated against known chunk IDs",
            ],
            "phase1_contracts": [
                "health and readiness endpoints",
                "workspace and document registration",
                "incremental chunk preview with content hashes",
                "rule pack library and deterministic applicability",
                "finding and report contracts",
                "support ticket triage contract",
                "AI model-route decision contract",
                "background job enqueue contract",
            ],
        }

    app.include_router(router)


app = create_service_app(
    "Evidence Hub API Gateway",
    description="North-south API boundary for the Evidence Hub web application.",
    configure=configure,
)
