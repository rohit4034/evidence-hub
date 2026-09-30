# Dokploy Deployment Notes

Use the root `docker-compose.yml` as the Dokploy Compose deployment source from GitHub. Do not upload the private `plan/` directory; this public repo is self-contained.

## Suggested Dokploy Flow

1. Create a new Compose project in Dokploy from GitHub: `rohit4034/evidence-hub`.
2. Use `docker-compose.yml` from the repository root.
3. Add environment variables in Dokploy using `.env.dokploy.example` as the checklist.
4. Set `PUBLIC_APP_URL` to the Dokploy public HTTPS URL for the web app.
5. Set `NVIDIA_API_KEY` only in Dokploy environment variables. Do not commit it.
6. Attach persistent volumes for Postgres, Redis, uploads, generated reports, and eval artifacts.
7. Deploy and check `/health` and `/ready` endpoints for the services.

## Public Service

The `web` service serves the React app on container port `80`. It proxies `/api/*` to `api-gateway:8000` through Nginx, so the browser only needs the web app URL.

For local testing, the compose file maps host port `3100` to web container port `80` because port `3000` may be occupied by Dokploy. In Dokploy, route traffic to the `web` service port `80`.

## Required Environment Variables

Core:

- `PUBLIC_APP_URL`
- `JWT_SECRET`
- `DEFAULT_DATA_USE_POLICY`
- `DATA_RETENTION_DAYS`

Storage:

- `POSTGRES_URL`
- `REDIS_URL`
- `FILE_STORAGE_PATH`
- `REPORT_STORAGE_PATH`
- `EVAL_STORAGE_PATH`

AI:

- `NVIDIA_API_KEY`
- `NVIDIA_BASE_URL`
- `AI_MODEL_CONFIG_SOURCE`
- `AI_MODEL_CONFIG_REFRESH_SECONDS`

Internal service URLs:

- `AI_SERVICE_URL`
- `EVIDENCE_SERVICE_URL`
- `COMPLIANCE_SERVICE_URL`
- `SUPPORT_SERVICE_URL`
- `WORKER_SERVICE_URL`

## Volumes To Preserve

- `postgres-data`
- `redis-data`
- `uploaded-files`
- `generated-reports`
- `eval-artifacts`

## Health Checks

From inside Dokploy or through service logs, each FastAPI service exposes:

- `/health`
- `/ready`

Externally, the web app should load first. Then use the `Run Demo` button to exercise the working vertical slice. The NVIDIA-backed AI summary requires `NVIDIA_API_KEY` to be configured.
