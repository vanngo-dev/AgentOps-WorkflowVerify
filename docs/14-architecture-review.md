# Phase 14 - Architecture Review

Phase 14 is the final documentation and architecture review phase for the AgentOps Workflow Verification Platform.

The project is now a local-first reference implementation for verifying deterministic agent workflows. It is ready for a new developer to run, test, inspect, and extend.

## System Overview

```text
Browser
  |
  | HTTP requests
  v
React/Vite frontend
  |
  | /api/workflow-runs
  v
FastAPI backend
  |
  | SQLAlchemy sessions
  v
PostgreSQL in Docker or SQLite in tests/E2E
```

The browser app creates and reviews workflow runs. The backend owns workflow state, simulated execution, validation, approval decisions, request IDs, and structured logs. The database stores the durable workflow record.

## Backend Architecture

```text
app/main.py
  |
  +-- request ID middleware
  +-- CORS middleware
  +-- health router
  +-- workflow run router

workflow run router
  |
  +-- SQLAlchemy session dependency
  +-- Pydantic request/response schemas
  +-- agent simulator service
  +-- approval decision handling
```

Important backend modules:

- `app/api/health.py` exposes `/health` and `/ready`.
- `app/api/workflow_runs.py` exposes workflow CRUD-style reads, execution, approval, and rejection.
- `app/services/agent_simulator.py` creates deterministic agent steps and final output payloads.
- `app/services/validation_engine.py` evaluates rules and sets risk/status.
- `app/middleware/request_id.py` assigns and returns request IDs.
- `app/core/request_context.py` stores the active trace ID for logs and response helpers.
- `app/db/session.py` owns SQLAlchemy engine and session setup.

## Frontend Architecture

```text
App.tsx
  |
  +-- Layout
  +-- HomePage
  +-- WorkflowRunsPage
  |     |
  |     +-- create workflow
  |     +-- list workflows
  |     +-- execute workflow
  |
  +-- WorkflowRunDetailPage
        |
        +-- summary and trace ID
        +-- input/output payloads
        +-- agent steps
        +-- validation results
        +-- approval history
        +-- approve/reject controls
```

The frontend keeps routing intentionally simple with browser history state in `App.tsx`. API calls are centralized in `frontend/src/api/workflowRuns.ts`.

## Database Model

```text
workflow_runs
  |
  +-- agent_steps
  +-- validation_results
  +-- approval_decisions
```

`workflow_runs` is the parent record. It stores name, status, risk level, input payload, output payload, and timestamps.

`agent_steps` records each deterministic simulator step with input and output snapshots.

`validation_results` records rule outcomes, severity, messages, and timestamps.

`approval_decisions` records human approval or rejection decisions with reviewer metadata.

## Workflow Lifecycle

```text
created
  |
  | execute
  v
running
  |
  | agent steps + validation
  v
completed
```

Other possible terminal or waiting states:

```text
created -> running -> validation_failed
created -> running -> approval_required -> approved
created -> running -> approval_required -> rejected
```

All workflow runs start with:

- `status=created`
- `risk_level=unknown`
- `output_payload=null`
- `completed_at=null`

## Agent Simulator Lifecycle

```text
inspect_input
  -> classify_document
  -> extract_fields
  -> calculate_risk
  -> produce_decision
```

The simulator is deterministic. It uses the workflow input payload and produces stable output every time for the same input.

Each step creates an `agent_steps` row with:

- `step_index`
- `step_name`
- `input_snapshot`
- `output_snapshot`
- `status=completed`
- timestamps

## Validation Lifecycle

```text
workflow output
  |
  v
validation rules
  |
  +-- required_vendor_present
  +-- required_invoice_id_present
  +-- amount_is_positive
  +-- decision_is_valid
  +-- high_amount_requires_review
  |
  v
risk_level + workflow status
```

Risk levels:

- `low` for positive amounts under 1000
- `medium` for amounts from 1000 up to 4999.99
- `high` for amounts 5000 or greater
- `unknown` for missing, invalid, or non-positive amounts

Status outcomes:

- validation errors set `validation_failed`
- high risk with no errors sets `approval_required`
- otherwise the workflow becomes `completed`

## Approval Lifecycle

```text
approval_required
  |
  +-- approve -> approved
  |
  +-- reject  -> rejected
```

Approval and rejection are only valid when a workflow is waiting in `approval_required`.

The backend stores each decision in `approval_decisions`, updates workflow status, sets `completed_at`, and logs the decision event.

## Trace And Observability Lifecycle

```text
HTTP request
  |
  | X-Request-ID present?
  | yes -> reuse value
  | no  -> generate UUID
  v
request.state.trace_id + context var
  |
  +-- response header X-Request-ID
  +-- structured workflow logs
  +-- workflow detail trace_id field
```

Structured logs include stable key-value fields:

```text
event=workflow_created trace_id=... workflow_run_id=...
event=workflow_execution_start trace_id=... workflow_run_id=...
event=agent_step_completed trace_id=... workflow_run_id=... step_name=...
event=validation_summary trace_id=... workflow_run_id=...
event=approval_decision_recorded trace_id=... workflow_run_id=...
```

The implementation avoids logging full payloads so workflow data is not duplicated into logs.

## Testing Strategy

```text
backend unit/API tests
  + frontend unit tests
  + frontend build
  + Playwright E2E
  + Docker Compose config validation
  = phase gate confidence
```

Backend tests use Pytest and SQLite-backed database setup where practical. They cover health endpoints, models, API behavior, execution, validation, approval, workflow detail, and request IDs.

Frontend tests use Vitest and Testing Library. They cover app routing, dashboard behavior, detail rendering, approval actions, and trace ID display.

Playwright E2E tests prove the real browser-to-backend workflow for low-risk completion and high-risk approval.

## Docker Strategy

```text
docker compose up --build
  |
  +-- postgres
  +-- backend
  |     +-- alembic upgrade head
  |     +-- uvicorn on port 8000
  |
  +-- frontend
        +-- vite on port 5173
```

Compose is local/dev oriented. It gives developers a repeatable stack without requiring them to install PostgreSQL directly.

The frontend calls `http://localhost:8000` from the browser. The backend calls PostgreSQL through the Compose service name `postgres`.

## CI Strategy

GitHub Actions runs on `push` and `pull_request`.

Jobs:

- backend tests and lint
- frontend tests and build
- Playwright E2E
- Docker Compose config validation

CI does not deploy the app. It provides a shared quality gate for the phase-gated project.

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

## Final Review

The project now demonstrates the core AgentOps control loop:

```text
create workflow
  -> execute deterministic agent
  -> record trace evidence
  -> validate results
  -> require approval when risk is high
  -> inspect and verify the run
```

Phase 14 stops here. Future phases or follow-up projects can add real model providers, asynchronous execution, production auth, richer observability, and deployment environments.
