from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class WorkspaceSummary(BaseModel):
    workspace_id: str
    name: str
    data_use_policy: str = "customer_private"


class WorkspaceCreate(BaseModel):
    name: str
    data_use_policy: Literal["customer_private", "eval_opt_in", "training_opt_in"] = "customer_private"


class DocumentUploadContract(BaseModel):
    workspace_id: str
    filename: str
    content_type: str
    source_uri: Optional[str] = None
    document_type: Optional[str] = None
    jurisdiction: Optional[str] = None
    domain: Optional[str] = None


class DocumentSummary(BaseModel):
    document_id: str
    workspace_id: str
    latest_version_id: str
    filename: str
    content_type: str
    status: str = "uploaded"
    created_at: datetime


class EvidenceChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_version_id: str
    workspace_id: str
    content_hash: str
    section_path: list[str] = Field(default_factory=list)
    page_number: Optional[int] = None
    text: str
    embedding_model: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None




class ChunkPreviewRequest(BaseModel):
    document_id: str
    document_version_id: str
    workspace_id: str
    text: str
    section_path: list[str] = Field(default_factory=list)
    page_number: Optional[int] = None
    embedding_model: Optional[str] = None


class IncrementalIndexPlan(BaseModel):
    workspace_id: str
    document_id: str
    document_version_id: str
    new_chunk_ids: list[str] = Field(default_factory=list)
    reused_chunk_ids: list[str] = Field(default_factory=list)
    chunks: list[EvidenceChunk] = Field(default_factory=list)


class RetrievalRequest(BaseModel):
    workspace_id: str
    query: str
    review_id: Optional[str] = None
    domain: Optional[str] = None
    jurisdiction: Optional[str] = None
    document_type: Optional[str] = None
    limit: int = Field(default=5, ge=1, le=50)


class RetrievalResult(BaseModel):
    chunk_id: str
    document_id: str
    score: float
    citation_label: str
    text: str


class CitationValidationRequest(BaseModel):
    cited_chunk_ids: list[str]
    available_chunk_ids: list[str]


class CitationValidationResponse(BaseModel):
    valid: bool
    missing_chunk_ids: list[str] = Field(default_factory=list)
