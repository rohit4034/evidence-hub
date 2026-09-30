# Evidence Hub

Evidence Hub is a multi-service platform for evidence-backed document intelligence, compliance review, support triage, and report generation.

Phase 1 provides the runnable foundation:

- Monorepo structure for web, services, packages, and infrastructure.
- Docker Compose for local use and GitHub-backed Dokploy setup.
- React app shell for operational product screens.
- FastAPI services with health, readiness, and concrete Phase 1 contracts.
- Shared Pydantic schemas for evidence, compliance, AI, support, and jobs.
- Evidence workspace, document, incremental chunking, retrieval, and citation validation contracts.
- Compliance rule pack, applicability, finding, and report contracts.
- Support triage and worker queue contracts.
- AI service runtime model-route configuration loader and deterministic route-decision endpoint.
- Admin-safe model route schema that redacts secrets and exposes routing state.
- Postgres/pgvector schema for Phase 1 records, AI traces, evals, data-use controls, and jobs.

## Prerequisites

- Node.js 20 LTS
- Python 3.11+
- Docker Desktop or Docker Engine

If you are using `n`, run:

```bash
export PATH="$HOME/.n/bin:$PATH"
# or use nvm / fnm to select Node 20
n 20.11.1
```

## Quick Start

```bash
cp .env.example .env
# Add NVIDIA_API_KEY in .env when you are ready to call NVIDIA NIM from the AI service.
docker compose up --build
```

`NVIDIA_API_KEY` is consumed only by the internal AI service. Other product services use the AI service boundary and never need direct NVIDIA credentials.

Services:

- Web: http://localhost:3100
- API Gateway: http://localhost:8000
- AI Service: http://localhost:8001
- Evidence Service: http://localhost:8002
- Compliance Service: http://localhost:8003
- Support Service: http://localhost:8004
- Worker Service: http://localhost:8005

## Local Development

Python services use the shared `evidence_hub_schemas` package and the common service bootstrap in `services/common`.

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r services/requirements.txt
uvicorn services.api_gateway.app.main:app --reload --port 8000
```

The web app is a Vite React application:

```bash
cd apps/web
npm install
npm run dev
```


## Phase 1 API Contracts

- Gateway: `GET /phase1`, `GET /services`
- Evidence: `POST /evidence/workspaces`, `POST /evidence/documents`, `POST /evidence/chunks/preview`, `POST /evidence/retrieval/search`, `POST /evidence/citations/validate`
- Compliance: `GET /compliance/rule-packs`, `POST /compliance/reviews`, `POST /compliance/findings/draft`, `POST /compliance/reports/contract`
- AI: `GET /model-routes`, `POST /model-routes/reload`, `POST /ai/route`, `POST /ai/chat`, `GET /ai/secret-status`
- Support: `POST /support/triage`
- Worker: `GET /jobs/queues`, `POST /jobs`

## Dokploy Setup

This repo is intended to be pushed to GitHub and then connected in Dokploy as a Docker Compose project. Do not copy private planning notes from `plan/` into the public repository. In Dokploy, set environment variables from `.env.example`, provide `NVIDIA_API_KEY`, and keep the Postgres, Redis, upload, report, and eval volumes attached.

## Verification

```bash
PYTHONPATH=.:packages/schemas pytest tests
npm run build:web
```

The working web app uses `/api/*` through the gateway. In local Vite development this is proxied by Vite; in Docker/Dokploy this is proxied by Nginx to `api-gateway:8000`.
