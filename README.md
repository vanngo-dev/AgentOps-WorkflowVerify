# AgentOps Workflow Verification Platform

The AgentOps Workflow Verification Platform is a phase-gated learning project for building the operational controls around AI-agent workflows.

It demonstrates how to create, execute, validate, inspect, approve, reject, test, observe, and run a deterministic agent workflow before introducing real LLM calls or production infrastructure.

The project is intentionally local-first and tutorial-shaped. Each phase is implemented, tested, documented, committed, and stopped before the next phase begins.

## What The Platform Demonstrates

- Workflow run creation and persistence
- Deterministic simulated agent execution
- Agent step trace capture
- Validation rules and risk classification
- Human approval and rejection paths
- Workflow detail inspection from the browser
- Playwright browser-to-backend E2E tests
- Local Docker Compose environment
- GitHub Actions CI quality gates
- Lightweight request IDs and structured workflow logs

## Tech Stack

- Backend: Python 3.12, FastAPI, SQLAlchemy, Alembic, Pydantic Settings
- Database: PostgreSQL for local Docker development, SQLite for isolated tests and E2E runtime data
- Frontend: React, TypeScript, Vite
- Tests: Pytest, Ruff, Vitest, Testing Library, Playwright
- Local stack: Docker Compose with PostgreSQL, backend, and frontend services
- CI: GitHub Actions for backend, frontend, Playwright E2E, and Compose config validation

## Final Project Status

Phases 00 through 14 are complete.

The final implementation includes the backend API, database model, deterministic agent simulator, validation engine, human approval flow, React dashboard and detail pages, Playwright E2E tests, Docker Compose local environment, GitHub Actions CI, and lightweight observability with request IDs and structured logs.

Phase 14 is documentation and architecture review only. It does not add real LLM calls, background workers, production authentication, deployment automation, or new product features.

## Phase-Gated Workflow

Every phase follows the same rule:

1. Implement the scoped work.
2. Run the relevant checks.
3. Document what changed.
4. Commit the phase.
5. Stop before starting the next phase.

That process mirrors the platform's own purpose: visible, reviewable, controlled workflow progression.

## Repository Guide

Start here:

- `docs/00-project-overview.md`
- `docs/14-architecture-review.md`
- `docs/final-verification-checklist.md`
- `docs/glossary.md`
- `backend/README.md`
- `frontend/README.md`

Phase docs:

- `docs/01-backend-foundation.md`
- `docs/02-database-model.md`
- `docs/03-workflow-api.md`
- `docs/04-agent-simulator.md`
- `docs/05-validation-engine.md`
- `docs/06-human-approval.md`
- `docs/07-frontend-shell.md`
- `docs/08-workflow-dashboard.md`
- `docs/09-workflow-detail-trace-viewer.md`
- `docs/10-e2e-tests.md`
- `docs/11-docker-compose.md`
- `docs/12-github-actions-ci.md`
- `docs/13-observability-structured-logs.md`
- `docs/14-architecture-review.md`

## Backend Setup

From the backend folder:

```sh
cd backend
python -m pip install -e .
```

For local PostgreSQL development, configure `DATABASE_URL` and run migrations:

```sh
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Default backend URL:

```text
http://localhost:8000
```

Health checks:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Frontend Setup

From the frontend folder:

```sh
cd frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://localhost:5173/workflow-runs
```

The frontend reads `VITE_API_BASE_URL`. For local development, use:

```text
VITE_API_BASE_URL=http://localhost:8000
```

## Docker Setup

From the repository root:

```sh
docker compose up --build
```

Services:

- `postgres` stores workflow data in the `postgres_data` named volume.
- `backend` runs migrations and serves FastAPI on `http://localhost:8000`.
- `frontend` runs Vite on `http://localhost:5173`.

Useful commands:

```sh
docker compose down
docker compose down -v
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
docker compose exec backend python -m alembic upgrade head
```

## Test Commands

Backend:

```sh
cd backend
python -m pytest
python -m ruff check .
```

Frontend:

```sh
cd frontend
npm test
npm run build
```

Playwright E2E:

```sh
cd frontend
npm run playwright:install
npm run test:e2e
```

Docker Compose validation:

```sh
docker compose config
```

Makefile shortcuts:

```sh
make help
make test
make lint
make docs
```

## CI Overview

GitHub Actions runs on `push` and `pull_request`.

The workflow includes:

- backend tests with `python -m pytest`
- backend lint with `python -m ruff check .`
- frontend unit tests with `npm test`
- frontend build with `npm run build`
- Playwright E2E with `npm run test:e2e`
- Docker Compose config validation with `docker compose config`

Do not treat CI as passed until the GitHub Actions run has completed successfully on GitHub.

## Observability And Trace IDs

Every backend request receives an `X-Request-ID` response header.

If a caller sends `X-Request-ID`, the backend reuses it. Otherwise, the backend generates a UUID.

Workflow logs use key-value fields such as:

```text
event=workflow_execution_start trace_id=... workflow_run_id=...
event=agent_step_completed trace_id=... workflow_run_id=... step_name=...
event=validation_summary trace_id=... workflow_run_id=... risk_level=...
```

Workflow detail responses include `trace_id`, and the frontend displays it on the detail page when present.

## Common Local Development Commands

```sh
cd backend
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

```sh
cd frontend
npm run dev
```

```sh
cd frontend
npm run test:e2e
```

```sh
docker compose up --build
docker compose down
docker compose down -v
```

## Current Limitations

- Deterministic simulated agent only
- No production authentication yet
- No background worker yet
- Local/dev Docker setup
- Simple validation rules
- Lightweight observability only
- No real deployment environment yet

## Suggested Improvements / Future Roadmap

These are practical next steps, not current features. The current project is a local-first verification platform with a deterministic simulated agent.

### 1. Real Agent / LLM Adapter

The current system uses a deterministic simulated agent so workflow behavior is stable and easy to test.

A future agent layer could use a provider interface with implementations such as:

- `SimulatedAgentProvider`
- `OpenAIProvider`
- `OllamaProvider`
- `LocalModelProvider`

Real LLM integration should preserve the current validation, trace, approval, and testing model. The model provider can change, but workflow evidence and safety gates should remain first-class.

### 2. Background Execution

Workflow execution currently happens in the request cycle. That is simple for this version, but longer agent runs should eventually move to a worker.

Possible options:

- Celery
- RQ
- Dramatiq
- Arq
- Redis-backed job queue

Expected future flow:

```text
POST /execute -> queued -> worker runs -> frontend polls or subscribes to status
```

### 3. OpenTelemetry And Metrics

The current request IDs and structured logs are lightweight observability.

Future observability could add:

- OpenTelemetry traces
- trace spans per agent step
- workflow duration metrics
- validation failure rates
- approval latency
- dashboard for operational metrics

### 4. Role-Based Access Control

The approval flow currently has reviewer fields, but no authenticated user roles.

Future roles could include:

- operator
- reviewer
- admin

Approval and rejection actions should eventually require reviewer or admin permissions so high-risk decisions are tied to authorized users.

### 5. Authentication And Production Security

Production use would need security work that is intentionally outside this version.

Missing production concerns include:

- authentication
- authorization
- secrets management
- rate limiting
- audit log hardening
- secure CORS configuration

### 6. File Upload And Ingestion

The current create form accepts structured invoice-like fields.

Future ingestion could support:

- JSON upload
- CSV upload
- invoice-like structured input
- PDF metadata placeholder
- validation before workflow creation

### 7. Benchmark / Evaluation Suite

As soon as real LLM providers are added, repeatable evaluation becomes more important.

A benchmark case could include:

- input case
- expected decision
- expected risk level
- expected validation results
- pass/fail result

This would make provider changes and prompt changes easier to compare.

### 8. Deployment Path

The current Docker setup is for local development.

Future deployment options could include:

- Docker Compose production-like environment
- Render, Fly.io, or Railway style deployment
- AWS ECS or Azure Container Apps
- managed Postgres
- CI/CD deployment workflow

### 9. Workflow Templates

The current workflow is invoice-review shaped.

Future templates could cover:

- vendor review
- customer support triage
- purchase order review
- document intake
- compliance checklist

### 10. Frontend UX Improvements

The frontend is intentionally straightforward. Useful next improvements could include:

- filtering by status or risk
- search
- pagination
- status badges
- better JSON viewer
- timeline visualization
- retry/re-run design with strict audit rules
