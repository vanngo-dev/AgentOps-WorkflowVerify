# Phase 13 - Observability And Structured Logs

## What We Build In This Phase

Phase 13 adds lightweight observability for local development and CI-safe testing.

We add:

- request and trace ID middleware
- `X-Request-ID` response headers
- optional trace ID display on workflow detail pages
- structured workflow logs
- backend and frontend tests for the trace ID behavior

We do not add OpenTelemetry, real LLM calls, background workers, or new app behavior.

## What Observability Means Here

Observability is the ability to understand what happened inside a workflow after a request is made.

For this project, that means each browser-to-backend request can be followed through workflow creation, execution, validation, and approval logs.

## Why Structured Logs Matter For Agent Workflows

Agent workflows are multi-step. A single user action may create a workflow run, simulate several agent steps, validate outputs, and wait for human approval.

Structured logs make those transitions searchable because each log line uses stable fields such as:

```text
event=workflow_execution_start trace_id=... workflow_run_id=...
event=agent_step_completed trace_id=... workflow_run_id=... step_name=...
event=validation_summary trace_id=... workflow_run_id=... risk_level=...
```

## Request And Trace IDs

Every HTTP request receives a trace ID.

If the request includes:

```text
X-Request-ID: custom-id
```

the backend reuses that value. Otherwise, it generates a UUID.

Every response includes:

```text
X-Request-ID: <trace id>
```

Workflow detail responses also include `trace_id`, which the frontend displays on the workflow detail page.

## Logged Workflow Events

The backend logs:

- workflow creation
- execution request and execution start
- each simulated agent step created and completed
- validation summary and resulting workflow status
- approval or rejection decisions
- practical API errors such as missing workflows or invalid state transitions

Logs intentionally avoid full input and output payloads so invoices, comments, and future sensitive data are not duplicated into application logs.

## How To See Logs Locally

Start the backend:

```sh
cd backend
python -m uvicorn app.main:app --reload
```

Start the frontend:

```sh
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173/workflow-runs
```

Create and execute a workflow, then watch the backend terminal for `event=...` log lines.

## Curl Verification

Generated request ID:

```sh
curl -i http://localhost:8000/health
```

Provided request ID:

```sh
curl -i -H "X-Request-ID: local-trace-1" http://localhost:8000/health
```

Detail response trace ID:

```sh
curl -i -H "X-Request-ID: detail-trace-1" http://localhost:8000/api/workflow-runs/1
```

The response header should include the same `X-Request-ID`. For workflow detail responses, the JSON body should include `trace_id`.

## Frontend Behavior

The workflow detail page shows a Trace ID field when the backend includes `trace_id`.

If a page was loaded from an endpoint that only exposes the response header, the trace ID is still available in browser network tools but is not displayed in the UI.

## Tests

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

Playwright E2E remains available:

```sh
cd frontend
npm run test:e2e
```

## Docker And CI Notes

Docker Compose and GitHub Actions use the same application entry points, so the request ID middleware and logs apply there too.

No Compose service or CI job is redesigned in this phase.

## Common Issues

If `X-Request-ID` is missing, confirm the request is reaching the FastAPI app and not failing before middleware startup.

If the frontend does not show a trace ID, confirm the browser is on a workflow detail page and the backend response body includes `trace_id`.

If logs do not include workflow IDs, confirm the request reached a workflow endpoint and not only `/health` or `/ready`.

If log output is too quiet, check the backend `LOG_LEVEL` setting.

## Manual Verification Scenarios

1. Open the dashboard and create a low-risk workflow.
2. Execute it and verify it becomes `completed` with `low` risk.
3. Open detail and verify trace ID, payloads, agent steps, and validations.
4. Create a high-risk workflow.
5. Execute it and verify it becomes `approval_required` with `high` risk.
6. Open detail, approve it, and verify approval history.
7. Confirm backend logs include matching `trace_id` and `workflow_run_id` fields.

## Next Phase Preview

Phase 14 can build on these trace IDs and structured logs.

Phase 13 stops here.
