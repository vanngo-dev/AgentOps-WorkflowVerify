# Backend

This folder contains the FastAPI backend foundation, database model layer, workflow run API, deterministic agent simulator, validation engine, human approval flow, workflow detail API, and Docker backend image definition.

Phase 11 adds a Dockerfile used by the root Compose stack. It keeps the local virtualenv workflow available and does not add real LLM calls, background workers, or observability infrastructure.

## Structure

```text
backend/
  app/
    main.py
    api/
      health.py
      workflow_runs.py
    core/
      config.py
      logging.py
    db/
      base.py
      session.py
    models/
      workflow_run.py
      agent_step.py
      validation_result.py
      approval_decision.py
    schemas/
      agent_step.py
      approval_decision.py
      validation_result.py
      workflow_run.py
    services/
      agent_simulator.py
      validation_engine.py
    tests/
      test_health.py
      test_models.py
      test_workflow_runs_api.py
      test_agent_simulator.py
      test_workflow_execution_api.py
      test_validation_engine.py
      test_human_approval_api.py
      test_workflow_detail_api.py
  alembic/
  Dockerfile
  pyproject.toml
  README.md
```

## Run Locally

Install the backend dependencies in your Python environment, then run:

```sh
uvicorn app.main:app --reload
```

Check the health endpoints:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected responses:

```json
{"status":"ok"}
{"status":"ready"}
```

Create and read workflow runs:

```sh
curl -X POST http://localhost:8000/api/workflow-runs ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"sample invoice review\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":1250,\"invoice_id\":\"INV-1001\"}}"

curl http://localhost:8000/api/workflow-runs
curl http://localhost:8000/api/workflow-runs/1
curl -X POST http://localhost:8000/api/workflow-runs/1/execute
curl -X POST http://localhost:8000/api/workflow-runs/1/approve ^
  -H "Content-Type: application/json" ^
  -d "{\"reviewer_name\":\"local reviewer\",\"comment\":\"Approved after review.\"}"
```

These workflow endpoints need a migrated database. For normal development, use PostgreSQL and run `alembic upgrade head` first.

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

Check backend health from the host:

```sh
curl http://localhost:8000/health
```

## Test

From this folder:

```sh
pytest
ruff check .
```

If those console scripts are not on your PATH, use:

```sh
python -m pytest
python -m ruff check .
```

## Database Migrations

Set `DATABASE_URL` to a PostgreSQL database URL for normal development:

```sh
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/agentops_workflow
```

Then run:

```sh
alembic upgrade head
```

If the console script is not on your PATH, run the Alembic executable from your active environment, such as:

```sh
.\.venv\Scripts\alembic.exe upgrade head
```

The model tests use SQLite so they can run without a local PostgreSQL server.
