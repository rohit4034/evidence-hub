from __future__ import annotations

from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class ServiceSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    service_name: str = Field(default="evidence-hub-service", alias="SERVICE_NAME")
    public_app_url: str = Field(default="http://localhost:3000", alias="PUBLIC_APP_URL")
    postgres_url: str = Field(
        default="postgresql://evidence:evidence@localhost:5432/evidence_hub",
        alias="POSTGRES_URL",
    )
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    file_storage_path: str = Field(default="/tmp/evidence-hub/uploads", alias="FILE_STORAGE_PATH")
    default_data_use_policy: str = Field(default="customer_private", alias="DEFAULT_DATA_USE_POLICY")
    data_retention_days: int = Field(default=365, alias="DATA_RETENTION_DAYS")
    ai_service_url: Optional[str] = Field(default=None, alias="AI_SERVICE_URL")
    evidence_service_url: Optional[str] = Field(default=None, alias="EVIDENCE_SERVICE_URL")
    compliance_service_url: Optional[str] = Field(default=None, alias="COMPLIANCE_SERVICE_URL")
    support_service_url: Optional[str] = Field(default=None, alias="SUPPORT_SERVICE_URL")
    worker_service_url: Optional[str] = Field(default=None, alias="WORKER_SERVICE_URL")
    nvidia_api_key: Optional[str] = Field(default=None, alias="NVIDIA_API_KEY")
    nvidia_base_url: str = Field(default="https://integrate.api.nvidia.com/v1", alias="NVIDIA_BASE_URL")
    ai_model_config_source: str = Field(
        default="/app/config/model-routes.json",
        alias="AI_MODEL_CONFIG_SOURCE",
    )
    ai_model_config_refresh_seconds: int = Field(default=30, alias="AI_MODEL_CONFIG_REFRESH_SECONDS")


@lru_cache
def get_settings() -> ServiceSettings:
    return ServiceSettings()

