from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from evidence_hub_schemas.ai import AdminSafeModelConfig, AdminSafeModelRoute, ModelRouteConfig
from services.common.settings import ServiceSettings


class ModelConfigLoader:
    def __init__(self, settings: ServiceSettings):
        self.settings = settings
        self._config: Optional[ModelRouteConfig] = None
        self._loaded_at: Optional[datetime] = None
        self._source_snapshot: Optional[str] = None

    def load(self, *, force: bool = False) -> ModelRouteConfig:
        source = self.settings.ai_model_config_source
        if self._config is not None and self._source_snapshot == source and not force:
            return self._config

        path = Path(source)
        data = json.loads(path.read_text(encoding="utf-8"))
        config = ModelRouteConfig.model_validate(data)
        self._config = config
        self._source_snapshot = source
        self._loaded_at = datetime.now(timezone.utc)
        return config

    def admin_safe(self) -> AdminSafeModelConfig:
        config = self.load()
        loaded_at = self._loaded_at or datetime.now(timezone.utc)
        return AdminSafeModelConfig(
            version=config.version,
            default_provider=config.default_provider,
            source=self.settings.ai_model_config_source,
            loaded_at=loaded_at.isoformat(),
            refresh_seconds=self.settings.ai_model_config_refresh_seconds,
            routes=[
                AdminSafeModelRoute(
                    route=route.route,
                    provider=route.provider,
                    model=route.model,
                    enabled=route.enabled,
                    priority=route.priority,
                    base_url_host=_host_only(str(route.base_url)) if route.base_url else None,
                    timeout_seconds=route.timeout_seconds,
                    max_input_tokens=route.max_input_tokens,
                    max_output_tokens=route.max_output_tokens,
                    json_schema_required=route.json_schema_required,
                    prompt_version=route.prompt_version,
                    tags=route.tags,
                )
                for route in sorted(config.routes, key=lambda item: (item.route.value, item.priority))
            ],
        )


def _host_only(url: str) -> Optional[str]:
    parsed = urlparse(url)
    return parsed.netloc or None

