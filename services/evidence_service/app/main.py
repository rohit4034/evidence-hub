from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import uuid5, NAMESPACE_URL

from fastapi import APIRouter, FastAPI

from evidence_hub_schemas.evidence import (
    ChunkPreviewRequest,
    CitationValidationRequest,
    CitationValidationResponse,
    DocumentSummary,
    DocumentUploadContract,
    EvidenceChunk,
    IncrementalIndexPlan,
    RetrievalRequest,
    RetrievalResult,
    WorkspaceCreate,
    WorkspaceSummary,
)
from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings

WORKSPACES: dict[str, WorkspaceSummary] = {
    "ws-demo": WorkspaceSummary(workspace_id="ws-demo", name="Demo workspace")
}
DOCUMENTS: dict[str, DocumentSummary] = {}
CHUNKS: dict[str, EvidenceChunk] = {}


def _stable_id(prefix: str, value: str) -> str:
    return f"{prefix}_{uuid5(NAMESPACE_URL, value).hex[:12]}"


def _content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(prefix="/evidence", tags=["evidence"])

    @router.get("/capabilities")
    def capabilities() -> dict[str, list[str]]:
        return {
            "accepted_inputs": ["pdf", "text", "markdown", "csv", "image"],
            "retrieval": ["keyword", "vector", "rerank"],
            "phase1_status": ["workspace_contracts", "document_versions", "incremental_chunk_plan", "citation_validation"],
        }

    @router.get("/workspaces", response_model=list[WorkspaceSummary])
    def list_workspaces() -> list[WorkspaceSummary]:
        return list(WORKSPACES.values())

    @router.post("/workspaces", response_model=WorkspaceSummary)
    def create_workspace(payload: WorkspaceCreate) -> WorkspaceSummary:
        workspace_id = _stable_id("ws", payload.name.lower())
        workspace = WorkspaceSummary(workspace_id=workspace_id, name=payload.name, data_use_policy=payload.data_use_policy)
        WORKSPACES[workspace_id] = workspace
        return workspace

    @router.post("/documents", response_model=DocumentSummary)
    def register_document(payload: DocumentUploadContract) -> DocumentSummary:
        seed = f"{payload.workspace_id}:{payload.filename}:{payload.source_uri or payload.content_type}"
        document_id = _stable_id("doc", seed)
        version_id = _stable_id("ver", f"{seed}:v1")
        document = DocumentSummary(
            document_id=document_id,
            workspace_id=payload.workspace_id,
            latest_version_id=version_id,
            filename=payload.filename,
            content_type=payload.content_type,
            created_at=datetime.now(timezone.utc),
        )
        DOCUMENTS[document_id] = document
        return document

    @router.post("/chunks/preview", response_model=IncrementalIndexPlan)
    def preview_chunks(payload: ChunkPreviewRequest) -> IncrementalIndexPlan:
        paragraphs = [part.strip() for part in payload.text.split("\n\n") if part.strip()] or [payload.text.strip()]
        new_chunk_ids: list[str] = []
        reused_chunk_ids: list[str] = []
        chunks: list[EvidenceChunk] = []
        for index, paragraph in enumerate(paragraphs, start=1):
            content_hash = _content_hash(paragraph)
            chunk_id = _stable_id("chk", f"{payload.workspace_id}:{payload.document_version_id}:{content_hash}")
            if chunk_id in CHUNKS:
                reused_chunk_ids.append(chunk_id)
                chunks.append(CHUNKS[chunk_id])
                continue
            chunk = EvidenceChunk(
                chunk_id=chunk_id,
                document_id=payload.document_id,
                document_version_id=payload.document_version_id,
                workspace_id=payload.workspace_id,
                content_hash=content_hash,
                section_path=payload.section_path or [f"chunk-{index}"],
                page_number=payload.page_number,
                text=paragraph,
                embedding_model=payload.embedding_model,
                valid_from=datetime.now(timezone.utc),
            )
            CHUNKS[chunk_id] = chunk
            new_chunk_ids.append(chunk_id)
            chunks.append(chunk)
        return IncrementalIndexPlan(
            workspace_id=payload.workspace_id,
            document_id=payload.document_id,
            document_version_id=payload.document_version_id,
            new_chunk_ids=new_chunk_ids,
            reused_chunk_ids=reused_chunk_ids,
            chunks=chunks,
        )

    @router.post("/retrieval/search", response_model=list[RetrievalResult])
    def search(payload: RetrievalRequest) -> list[RetrievalResult]:
        terms = {term.lower() for term in payload.query.split() if term}
        scored: list[RetrievalResult] = []
        for chunk in CHUNKS.values():
            if chunk.workspace_id != payload.workspace_id:
                continue
            haystack = chunk.text.lower()
            hits = sum(1 for term in terms if term in haystack)
            if hits == 0 and terms:
                continue
            scored.append(
                RetrievalResult(
                    chunk_id=chunk.chunk_id,
                    document_id=chunk.document_id,
                    score=float(hits or 0.1),
                    citation_label=" > ".join(chunk.section_path) or chunk.chunk_id,
                    text=chunk.text,
                )
            )
        return sorted(scored, key=lambda item: item.score, reverse=True)[: payload.limit]

    @router.post("/citations/validate", response_model=CitationValidationResponse)
    def validate_citations(payload: CitationValidationRequest) -> CitationValidationResponse:
        available = set(payload.available_chunk_ids)
        missing = [chunk_id for chunk_id in payload.cited_chunk_ids if chunk_id not in available]
        return CitationValidationResponse(valid=not missing, missing_chunk_ids=missing)

    app.include_router(router)


app = create_service_app(
    "Evidence Hub Evidence Service",
    description="Document and evidence ingestion boundary for Evidence Desk.",
    configure=configure,
)
