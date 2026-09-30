# Dokploy Notes

Use the root `docker-compose.yml` as the initial Dokploy Compose deployment.

Required Dokploy-managed values:

- `NVIDIA_API_KEY`
- `NVIDIA_BASE_URL`
- `AI_MODEL_CONFIG_SOURCE`
- `AI_MODEL_CONFIG_REFRESH_SECONDS`
- `POSTGRES_URL`
- `REDIS_URL`
- `JWT_SECRET`
- `FILE_STORAGE_PATH`
- `DATA_RETENTION_DAYS`
- `DEFAULT_DATA_USE_POLICY`
- `PUBLIC_APP_URL`

Persist these volumes:

- `postgres-data`
- `redis-data`
- `uploaded-files`
- `generated-reports`
- `eval-artifacts`

