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

## Limitations

- Deterministic simulated agent only
- No real LLM adapter yet
- No background worker yet
- No role-based access control yet
- No production authentication yet
- Local development focus
- Simple validation rules
- Limited observability compared with OpenTelemetry
- Docker setup is local/dev oriented
- E2E tests may require local services depending on configuration

## Future Improvements

- Real LLM adapter
- Provider interface for `SimulatedAgentProvider`, `OpenAIProvider`, `OllamaProvider`, and `LocalModelProvider`
- Background job queue
- OpenTelemetry tracing
- Metrics dashboard
- Role-based access control
- File upload ingestion
- Benchmark/evaluation suite
- Deployment environment
- Richer workflow templates
