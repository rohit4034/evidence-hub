from __future__ import annotations

import os

os.environ.setdefault("AI_MODEL_CONFIG_SOURCE", "services/ai-service/config/model-routes.json")
os.environ.setdefault("SERVICE_NAME", "test-service")

from fastapi.testclient import TestClient

from services.ai_service.app.main import app as ai_app
from services.compliance_service.app.main import app as compliance_app
from services.evidence_service.app.main import app as evidence_app


def test_evidence_incremental_chunk_plan_reuses_hashes() -> None:
    client = TestClient(evidence_app)
    document = client.post(
        "/evidence/documents",
        json={"workspace_id": "ws-demo", "filename": "policy.md", "content_type": "text/markdown"},
    ).json()

    payload = {
        "workspace_id": "ws-demo",
        "document_id": document["document_id"],
        "document_version_id": document["latest_version_id"],
        "text": "Access is reviewed quarterly.\n\nLogs are retained for 180 days.",
    }
    first = client.post("/evidence/chunks/preview", json=payload).json()
    second = client.post("/evidence/chunks/preview", json=payload).json()

    assert len(first["new_chunk_ids"]) == 2
    assert second["new_chunk_ids"] == []
    assert second["reused_chunk_ids"] == first["new_chunk_ids"]


def test_compliance_review_applies_dpdp_obligations() -> None:
    client = TestClient(compliance_app)
    response = client.post(
        "/compliance/reviews",
        json={
            "workspace_id": "ws-demo",
            "rule_pack_id": "india-dpdp-privacy",
            "answers": {"processes_personal_data": True},
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["applicable_obligation_ids"] == ["IN-DPDP-001", "IN-DPDP-002"]


def test_ai_route_escalates_high_risk_tasks_to_large_reasoning() -> None:
    client = TestClient(ai_app)
    response = client.post(
        "/ai/route",
        json={"task_type": "classification", "risk": "high", "input_token_estimate": 400},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["selected_route"] == "large_reasoning"
    assert body["model_provider"] == "nvidia"


def test_ai_secret_status_is_redacted() -> None:
    client = TestClient(ai_app)
    body = client.get("/ai/secret-status").json()

    assert body["api_key_value"] == "redacted"
