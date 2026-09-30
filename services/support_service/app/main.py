from __future__ import annotations

from uuid import uuid5, NAMESPACE_URL

from fastapi import APIRouter, FastAPI

from evidence_hub_schemas.support import SupportTicketImport, SupportTriageResult
from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:12]}"


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(prefix="/support", tags=["support"])

    @router.get("/capabilities")
    def capabilities() -> dict[str, list[str]]:
        return {
            "workflow": ["ticket_import", "classification", "clustering", "draft_replies", "trend_reports"],
            "phase1_status": ["ticket_contracts", "deterministic_triage", "human_draft_boundary"],
        }

    @router.post("/triage", response_model=SupportTriageResult)
    def triage(payload: SupportTicketImport) -> SupportTriageResult:
        text = f"{payload.subject} {payload.body}".lower()
        if any(term in text for term in ["breach", "incident", "security", "down"]):
            category, priority = "security_or_availability", "urgent"
        elif any(term in text for term in ["privacy", "delete", "consent", "data"]):
            category, priority = "privacy_request", "high"
        elif any(term in text for term in ["invoice", "billing", "payment"]):
            category, priority = "billing", "medium"
        else:
            category, priority = "general_support", "medium"
        ticket_id = _stable_id("ticket", f"{payload.workspace_id}:{payload.external_id}")
        return SupportTriageResult(
            ticket_id=ticket_id,
            category=category,
            priority=priority,
            duplicate_cluster_id=_stable_id("cluster", category),
            summary=payload.subject[:160],
            draft_response="Thanks for the details. A reviewer should verify the supporting evidence before sending a final response.",
        )

    app.include_router(router)


app = create_service_app(
    "Evidence Hub Support Service",
    description="Support triage workflow boundary backed by Evidence Desk.",
    configure=configure,
)
