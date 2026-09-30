from __future__ import annotations

from fastapi import APIRouter, FastAPI, HTTPException

from evidence_hub_schemas.ai import (
    AITaskRequest,
    AITaskType,
    AdminSafeModelConfig,
    ModelClass,
    ModelRoute,
    RouteDecision,
)
from services.ai_service.app.model_config import ModelConfigLoader
from services.common.app_factory import create_service_app
from services.common.settings import ServiceSettings

TASK_ROUTE_MAP: dict[AITaskType, list[ModelClass]] = {
    AITaskType.classification: [ModelClass.classification, ModelClass.small_reasoning, ModelClass.large_reasoning],
    AITaskType.extraction: [ModelClass.extraction, ModelClass.small_reasoning, ModelClass.large_reasoning],
    AITaskType.compliance_gap_analysis: [ModelClass.large_reasoning],
    AITaskType.report_generation: [ModelClass.reporting, ModelClass.large_reasoning],
    AITaskType.screenshot_evidence_extraction: [ModelClass.vision_language, ModelClass.large_reasoning],
    AITaskType.embedding: [ModelClass.embedding],
    AITaskType.rerank: [ModelClass.rerank],
}


def _select_route(payload: AITaskRequest, routes: list[ModelRoute]) -> tuple[ModelRoute, list[ModelClass], str]:
    enabled = [route for route in routes if route.enabled]
    by_class: dict[ModelClass, list[ModelRoute]] = {}
    for route in enabled:
        by_class.setdefault(route.route, []).append(route)
    for candidates in by_class.values():
        candidates.sort(key=lambda item: item.priority)

    route_order = list(TASK_ROUTE_MAP[payload.task_type])
    reason = "task policy"
    if "image" in payload.modalities and ModelClass.vision_language not in route_order:
        route_order.insert(0, ModelClass.vision_language)
        reason = "image modality requires vision-capable route"
    if payload.risk == "high" and ModelClass.large_reasoning in by_class and ModelClass.large_reasoning not in route_order[:1]:
        route_order.insert(0, ModelClass.large_reasoning)
        reason = "high risk escalated to large reasoning"
    if payload.input_token_estimate > 12000 and ModelClass.large_reasoning in by_class:
        route_order.insert(0, ModelClass.large_reasoning)
        reason = "large input escalated to long-context reasoning"

    deduped: list[ModelClass] = []
    for route_class in route_order:
        if route_class not in deduped:
            deduped.append(route_class)

    for route_class in deduped:
        if route_class in by_class:
            return by_class[route_class][0], deduped[1:], reason
    raise HTTPException(status_code=422, detail="No enabled model route matched the task")


def configure(app: FastAPI, settings: ServiceSettings) -> None:
    router = APIRouter(prefix="/model-routes", tags=["model routes"])
    task_router = APIRouter(prefix="/ai", tags=["ai tasks"])
    loader = ModelConfigLoader(settings)

    @router.get("", response_model=AdminSafeModelConfig)
    def get_model_routes() -> AdminSafeModelConfig:
        return loader.admin_safe()

    @router.post("/reload", response_model=AdminSafeModelConfig)
    def reload_model_routes() -> AdminSafeModelConfig:
        loader.load(force=True)
        return loader.admin_safe()

    @task_router.post("/route", response_model=RouteDecision)
    def route_task(payload: AITaskRequest) -> RouteDecision:
        config = loader.load()
        selected, fallbacks, reason = _select_route(payload, config.routes)
        return RouteDecision(
            task_type=payload.task_type,
            selected_route=selected.route,
            fallback_routes=fallbacks,
            model_provider=selected.provider,
            model_name=selected.model,
            model_config_version=config.version,
            prompt_version=selected.prompt_version,
            reason=reason,
        )

    @task_router.get("/secret-status")
    def secret_status() -> dict[str, object]:
        return {"nvidia_api_key_configured": bool(settings.nvidia_api_key), "api_key_value": "redacted"}

    app.include_router(router)
    app.include_router(task_router)


app = create_service_app(
    "Evidence Hub AI Service",
    description="Internal AI service for configurable model routing, schemas, traces, and provider boundaries.",
    configure=configure,
)
