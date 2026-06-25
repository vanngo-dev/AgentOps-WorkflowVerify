# Backend

The backend is the FastAPI service for the AgentOps Workflow Verification Platform.

It owns workflow persistence, deterministic workflow execution, validation, human approval decisions, request IDs, and structured workflow logs.

## Structure

```text
backend/
  app/
    api/
      health.py
      workflow_runs.py
    core/
      config.py
      logging.py
      request_context.py
    db/
      base.py
      session.py
    middleware/
      request_id.py
    models/
      workflow_run.py
      agent_step.py
      validation_result.py
      approval_decision.py
    schemas/
    services/
      agent_simulator.py
      validation_engine.py
    tests/
  alembic/
  Dockerfile
  pyproject.toml
  README.md
```

## Run Locally

Install dependencies:

```sh
python -m pip install -e .
```

Set `DATABASE_URL` for local PostgreSQL development:

```sh
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/agentops_workflow
```

Run migrations and start the API:

```sh
python -m alembic upgrade head
python -m uvicorn app.main:app --reload
```

Health checks:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

## Workflow API

```sh
curl -X POST http://localhost:8000/api/workflow-runs \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"sample invoice review\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":500,\"invoice_id\":\"INV-1001\"}}"

curl http://localhost:8000/api/workflow-runs
curl http://localhost:8000/api/workflow-runs/1
curl -X POST http://localhost:8000/api/workflow-runs/1/execute
curl -X POST http://localhost:8000/api/workflow-runs/1/approve \
  -H "Content-Type: application/json" \
  -d "{\"reviewer_name\":\"local reviewer\",\"comment\":\"Approved after review.\"}"
curl -X POST http://localhost:8000/api/workflow-runs/1/reject \
  -H "Content-Type: application/json" \
  -d "{\"reviewer_name\":\"local reviewer\",\"comment\":\"Rejected after review.\"}"
```

## Observability

Every response includes `X-Request-ID`.

To provide your own trace ID:

```sh
curl -i http://localhost:8000/health -H "X-Request-ID: local-check-123"
```

Workflow operations log key-value events with `trace_id` and `workflow_run_id` where useful.

## Run With Docker Compose

From the repository root:

```sh
docker compose up --build
```

The backend container runs:

```sh
python -m alembic upgrade head
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Test

From this folder:

```sh
python -m pytest
python -m ruff check .
```

Tests use SQLite where practical so unit and API tests do not require local PostgreSQL.

## Migrations

Run migrations locally:

```sh
python -m alembic upgrade head
```

Run migrations in Docker:

```sh
docker compose exec backend python -m alembic upgrade head
```
