from __future__ import annotations

from uuid import uuid5, NAMESPACE_URL

from fastapi import APIRouter, FastAPI, HTTPException

from evidence_hub_schemas.compliance import (
    EvidenceMappingRequest,
    Finding,
    FindingStatus,
    Obligation,
    ReportContract,
    ReviewCreate,
    ReviewSummary,
    RulePack,
)
from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings

RULE_PACKS: dict[str, RulePack] = {
    "general-cybersecurity-baseline": RulePack(
        id="general-cybersecurity-baseline",
        name="General Cybersecurity Baseline",
        jurisdiction="Global",
        domain="Cybersecurity",
        version="2026.1",
        sources=["NIST CSF", "CIS Controls"],
        applicability_questions=[{"id": "handles_sensitive_data", "label": "Handles sensitive data", "type": "boolean"}],
        obligations=[
            Obligation(
                id="CYB-001",
                title="Maintain documented security governance",
                legal_basis=["NIST CSF Govern"],
                required_evidence=["security policy", "risk register", "owner list"],
                severity="high",
            ),
            Obligation(
                id="CYB-002",
                title="Retain security logs for investigations",
                legal_basis=["CIS Controls 8"],
                required_evidence=["logging policy", "SIEM screenshot", "retention configuration"],
            ),
        ],
    ),
    "india-dpdp-privacy": RulePack(
        id="india-dpdp-privacy",
        name="India DPDP / Privacy",
        jurisdiction="India",
        domain="Privacy",
        version="2026.1",
        sources=["Digital Personal Data Protection Act"],
        applicability_questions=[{"id": "processes_personal_data", "label": "Processes digital personal data", "type": "boolean"}],
        obligations=[
            Obligation(
                id="IN-DPDP-001",
                title="Provide notice before processing personal data",
                legal_basis=["DPDP notice obligations"],
                applies_when={"processes_personal_data": True},
                required_evidence=["privacy notice", "consent capture", "processing register"],
                severity="high",
            ),
            Obligation(
                id="IN-DPDP-002",
                title="Support data principal rights requests",
                legal_basis=["DPDP data principal rights"],
                applies_when={"processes_personal_data": True},
                required_evidence=["rights request SOP", "ticket samples"],
            ),
        ],
    ),
}
REVIEWS: dict[str, ReviewSummary] = {}
FINDINGS: dict[str, Finding] = {}


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:12]}"


def _applies(obligation: Obligation, answers: dict[str, object]) -> bool:
    return all(answers.get(key) == expected for key, expected in obligation.applies_when.items())


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(prefix="/compliance", tags=["compliance"])

    @router.get("/capabilities")
    def capabilities() -> dict[str, list[str]]:
        return {
            "workflow": ["rule_pack_library", "applicability", "obligation_review", "findings", "reports"],
            "phase1_status": ["rule_packs", "review_contracts", "deterministic_applicability", "finding_contracts"],
        }

    @router.get("/rule-packs", response_model=list[RulePack])
    def list_rule_packs() -> list[RulePack]:
        return list(RULE_PACKS.values())

    @router.get("/rule-packs/{rule_pack_id}", response_model=RulePack)
    def get_rule_pack(rule_pack_id: str) -> RulePack:
        if rule_pack_id not in RULE_PACKS:
            raise HTTPException(status_code=404, detail="Rule pack not found")
        return RULE_PACKS[rule_pack_id]

    @router.post("/reviews", response_model=ReviewSummary)
    def create_review(payload: ReviewCreate) -> ReviewSummary:
        rule_pack = RULE_PACKS.get(payload.rule_pack_id)
        if rule_pack is None:
            raise HTTPException(status_code=404, detail="Rule pack not found")
        applicable = [obligation.id for obligation in rule_pack.obligations if _applies(obligation, payload.answers)]
        review_id = _stable_id("rev", f"{payload.workspace_id}:{payload.rule_pack_id}:{sorted(payload.answers.items())}")
        review = ReviewSummary(
            review_id=review_id,
            workspace_id=payload.workspace_id,
            rule_pack_id=payload.rule_pack_id,
            applicable_obligation_ids=applicable,
        )
        REVIEWS[review_id] = review
        return review

    @router.post("/findings/draft", response_model=Finding)
    def draft_finding(payload: EvidenceMappingRequest) -> Finding:
        status = FindingStatus.partial if payload.candidate_chunk_ids else FindingStatus.missing
        finding = Finding(
            finding_id=_stable_id("fnd", f"{payload.review_id}:{payload.obligation_id}:{payload.candidate_chunk_ids}"),
            obligation_id=payload.obligation_id,
            status=status,
            summary="Evidence candidates require human review." if payload.candidate_chunk_ids else "No supporting evidence has been mapped yet.",
            citation_chunk_ids=payload.candidate_chunk_ids,
        )
        FINDINGS[finding.finding_id] = finding
        return finding

    @router.post("/reports/contract")
    def report_contract(payload: ReportContract) -> dict[str, object]:
        return {
            "review_id": payload.review_id,
            "format": payload.format,
            "sections": ["scope", "applicability", "findings", "citations", "reviewer_signoff"],
            "include_ai_trace": payload.include_ai_trace,
            "include_citations": payload.include_citations,
        }

    app.include_router(router)


app = create_service_app(
    "Evidence Hub Compliance Service",
    description="Rule packs, obligation reviews, findings, and report workflow boundary.",
    configure=configure,
)
