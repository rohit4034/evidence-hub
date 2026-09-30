from __future__ import annotations

from typing import Any

import httpx
from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, Response

from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings


def _service_map(settings: ServiceSettings) -> dict[str, str | None]:
    return {
        "evidence": settings.evidence_service_url,
        "compliance": settings.compliance_service_url,
        "ai": settings.ai_service_url,
        "model-routes": settings.ai_service_url,
        "support": settings.support_service_url,
        "jobs": settings.worker_service_url,
    }


async def _proxy(request: Request, base_url: str | None, target_path: str) -> Response:
    if not base_url:
        raise HTTPException(status_code=503, detail="Target service URL is not configured")

    body = await request.body()
    headers = {key: value for key, value in request.headers.items() if key.lower() not in {"host", "content-length"}}
    url = f"{base_url.rstrip('/')}/{target_path.lstrip('/')}"
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            upstream = await client.request(
                request.method,
                url,
                params=request.query_params,
                content=body or None,
                headers=headers,
            )
    except httpx.RequestError as exc:
        raise HTTPException(status_code=502, detail=f"Upstream service unavailable: {exc}") from exc

    media_type = upstream.headers.get("content-type")
    return Response(content=upstream.content, status_code=upstream.status_code, media_type=media_type)


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(tags=["gateway"])
    services = _service_map(settings)

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
            "status": "usable_vertical_slice",
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
                "workspace and document registration",
                "incremental chunk preview with content hashes",
                "evidence retrieval and citation validation",
                "rule pack library and deterministic applicability",
                "finding and report contracts",
                "support ticket triage contract",
                "AI model-route decision contract",
                "background job enqueue contract",
            ],
        }

    @router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def proxy_service(service: str, path: str, request: Request) -> Response:
        if service not in services:
            return JSONResponse(status_code=404, content={"detail": "Unknown gateway service"})
        target_path = f"/{service}/{path}" if path else f"/{service}"
        return await _proxy(request, services[service], target_path)

    app.include_router(router)


app = create_service_app(
    "Evidence Hub API Gateway",
    description="North-south API boundary for the Evidence Hub web application.",
    configure=configure,
)
