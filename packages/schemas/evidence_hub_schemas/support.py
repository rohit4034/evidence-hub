from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class SupportTicketImport(BaseModel):
    workspace_id: str
    external_id: str
    subject: str
    body: str
    source: Literal["csv", "email", "chat", "manual"] = "manual"
    customer_id: Optional[str] = None


class SupportTriageResult(BaseModel):
    ticket_id: str
    category: str
    priority: Literal["low", "medium", "high", "urgent"]
    duplicate_cluster_id: Optional[str] = None
    summary: str
    draft_response: str
    evidence_chunk_ids: list[str] = Field(default_factory=list)
