from __future__ import annotations

from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class FindingStatus(str, Enum):
    pass_ = "pass"
    partial = "partial"
    missing = "missing"
    unclear = "unclear"
    not_applicable = "not_applicable"


class Obligation(BaseModel):
    id: str
    title: str
    legal_basis: list[str] = Field(default_factory=list)
    applies_when: dict[str, Any] = Field(default_factory=dict)
    required_evidence: list[str] = Field(default_factory=list)
    assessment_questions: list[str] = Field(default_factory=list)
    severity: str = "medium"
    status_logic: str = "evidence_based"


class RulePack(BaseModel):
    id: str
    name: str
    jurisdiction: str
    domain: str
    version: str
    sources: list[str] = Field(default_factory=list)
    applicability_questions: list[dict[str, Any]] = Field(default_factory=list)
    obligations: list[Obligation] = Field(default_factory=list)
    report_templates: list[dict[str, Any]] = Field(default_factory=list)


class ReviewCreate(BaseModel):
    workspace_id: str
    rule_pack_id: str
    answers: dict[str, Any] = Field(default_factory=dict)


class ReviewSummary(BaseModel):
    review_id: str
    workspace_id: str
    rule_pack_id: str
    applicable_obligation_ids: list[str] = Field(default_factory=list)
    status: str = "draft"


class Finding(BaseModel):
    finding_id: str
    obligation_id: str
    status: FindingStatus
    summary: str
    citation_chunk_ids: list[str] = Field(default_factory=list)
    reviewer_status: str = "pending"




class EvidenceMappingRequest(BaseModel):
    review_id: str
    obligation_id: str
    candidate_chunk_ids: list[str] = Field(default_factory=list)
    reviewer_note: Optional[str] = None


class ReportContract(BaseModel):
    review_id: str
    format: str = "pdf"
    include_ai_trace: bool = True
    include_citations: bool = True
