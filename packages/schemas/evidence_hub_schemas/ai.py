from __future__ import annotations

from enum import Enum
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ModelClass(str, Enum):
    small_reasoning = "small_reasoning"
    large_reasoning = "large_reasoning"
    embedding = "embedding"
    rerank = "rerank"
    vision_language = "vision_language"
    vision_detection = "vision_detection"
    classification = "classification"
    extraction = "extraction"
    reporting = "reporting"


class AITaskType(str, Enum):
    classification = "classification"
    extraction = "extraction"
    compliance_gap_analysis = "compliance_gap_analysis"
    report_generation = "report_generation"
    screenshot_evidence_extraction = "screenshot_evidence_extraction"
    embedding = "embedding"
    rerank = "rerank"


class ModelRoute(BaseModel):
    route: ModelClass
    provider: str = Field(default="nvidia")
    model: str
    enabled: bool = True
    priority: int = Field(default=100, ge=0)
    base_url: Optional[HttpUrl] = None
    timeout_seconds: int = Field(default=60, ge=1, le=600)
    max_input_tokens: Optional[int] = Field(default=None, ge=1)
    max_output_tokens: Optional[int] = Field(default=None, ge=1)
    json_schema_required: bool = False
    prompt_version: str = "phase1-default"
    tags: list[str] = Field(default_factory=list)


class ModelRouteConfig(BaseModel):
    version: str
    default_provider: str = "nvidia"
    routes: list[ModelRoute]

    @field_validator("routes")
    @classmethod
    def require_enabled_route_per_class(cls, routes: list[ModelRoute]) -> list[ModelRoute]:
        enabled_classes = {route.route for route in routes if route.enabled}
        missing = [model_class.value for model_class in ModelClass if model_class not in enabled_classes]
        if missing:
            raise ValueError(f"missing enabled routes for: {', '.join(missing)}")
        return routes


class AdminSafeModelRoute(BaseModel):
    route: ModelClass
    provider: str
    model: str
    enabled: bool
    priority: int
    base_url_host: Optional[str] = None
    timeout_seconds: int
    max_input_tokens: Optional[int] = None
    max_output_tokens: Optional[int] = None
    json_schema_required: bool
    prompt_version: str
    tags: list[str]


class AdminSafeModelConfig(BaseModel):
    version: str
    default_provider: str
    source: str
    loaded_at: str
    refresh_seconds: int
    routes: list[AdminSafeModelRoute]


class AITraceEnvelope(BaseModel):
    request_id: str
    model_provider: str
    model_name: str
    model_route: ModelClass
    model_config_version: str
    prompt_version: str
    latency_ms: Optional[int] = None
    estimated_cost: Optional[float] = None
    status: Literal["accepted", "completed", "failed"] = "accepted"
    metadata: dict[str, Any] = Field(default_factory=dict)




class AITaskRequest(BaseModel):
    task_type: AITaskType
    workspace_id: Optional[str] = None
    input_token_estimate: int = Field(default=0, ge=0)
    modalities: list[Literal["text", "image"]] = Field(default_factory=lambda: ["text"])
    risk: Literal["low", "medium", "high"] = "medium"
    requires_json_schema: bool = True


class RouteDecision(BaseModel):
    task_type: AITaskType
    selected_route: ModelClass
    fallback_routes: list[ModelClass] = Field(default_factory=list)
    model_provider: str
    model_name: str
    model_config_version: str
    prompt_version: str
    reason: str


class CitedAIOutput(BaseModel):
    answer: str
    confidence: float = Field(ge=0, le=1)
    evidence_chunk_ids: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    recommended_next_questions: list[str] = Field(default_factory=list)
    model: str
    model_route: ModelClass
    model_config_version: str
    prompt_version: str
