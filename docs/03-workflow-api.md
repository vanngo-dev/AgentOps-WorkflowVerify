# Phase 03 - Workflow Run API

## What We Build In This Phase

In Phase 03, we add the first real workflow REST API.

We build three endpoints:

- `POST /api/workflow-runs`
- `GET /api/workflow-runs`
- `GET /api/workflow-runs/{workflow_run_id}`

These endpoints let us create a workflow run, list workflow runs, and read one workflow run by ID. We do not execute workflows yet. We do not create agent steps, validation results, or approval decisions yet.

## Why This Phase Matters

The database from Phase 02 is useful, but users and other systems need a clean way to interact with it. That is what this API gives us.

This phase turns the `WorkflowRun` model into a small HTTP surface. It is the first point where the backend starts to feel like a platform instead of only a set of internal files.

## Mental Model

Think of a workflow run as a job envelope.

When a user creates one, they are saying, "Here is the work I want the platform to track." The platform records the name and input payload. It does not process the job yet.

Every new workflow run starts with:

- `status` set to `created`
- `risk_level` set to `unknown`
- `output_payload` set to `null`
- `completed_at` set to `null`

That gives later phases a clean starting point.

## Files Added Or Changed

Added:

- `backend/app/api/workflow_runs.py`
- `backend/app/schemas/workflow_run.py`
- `backend/app/schemas/__init__.py`
- `backend/app/tests/test_workflow_runs_api.py`
- `docs/03-workflow-api.md`

Changed:

- `Makefile`
- `README.md`
- `backend/README.md`
- `backend/app/main.py`

## Step-By-Step Walkthrough

First, we add Pydantic schemas in `backend/app/schemas/workflow_run.py`.

The create schema describes what the client is allowed to send. The response schema describes what the API sends back. This matters because clients should not send fields like `status` or `risk_level` when creating a run. The backend owns those defaults.

Next, we add `backend/app/api/workflow_runs.py`.

This router handles the three endpoints. It uses the database dependency from Phase 02, creates SQLAlchemy `WorkflowRun` records, commits them, and returns model objects through the response schema.

Then, we update `backend/app/main.py` to include the workflow run router.

Finally, we add API tests. The tests override the real database dependency with an isolated SQLite database, so they never depend on a developer's local PostgreSQL service.

## Key Code Concepts

REST API design means exposing resources through predictable HTTP endpoints. In this phase, the resource is a workflow run. `POST` creates a resource. `GET` lists or reads resources.

Workflow runs start as `created` because the platform has only recorded the request. No agent has executed yet.

`risk_level` starts as `unknown` because risk has not been evaluated yet. A later validation or risk phase can change it once the system has evidence.

Request schemas and response schemas keep the API contract clear. The request schema accepts only the fields needed to create a workflow run. The response schema includes the database-generated fields, defaults, and timestamps.

FastAPI validates bad input automatically. If the client leaves out the required `name`, FastAPI returns `422` before our endpoint tries to save anything.

SQLAlchemy saves workflow runs by creating a model object, adding it to the session, committing the transaction, and refreshing the object so generated fields like `id` and timestamps are available.

API tests prove the behavior by making HTTP-style requests to the FastAPI app, checking status codes, checking response bodies, and verifying that missing data returns validation errors.

## How To Run It

From the backend folder:

```sh
python -m uvicorn app.main:app --reload
```

The API will run at:

```text
http://localhost:8000
```

For normal development, make sure `DATABASE_URL` points to a database that has been migrated with Alembic.

If PostgreSQL is not running locally and you only want to try the API, you can temporarily use SQLite:

```powershell
$env:DATABASE_URL = "sqlite:///./phase03_manual_check.sqlite3"
alembic upgrade head
python -m uvicorn app.main:app --reload
```

## How To Test It

From the backend folder:

```sh
python -m pytest
python -m ruff check .
```

These commands use the active Python environment. The API tests use SQLite in memory, so they do not need local PostgreSQL.

## Manual Verification

Start the backend:

```sh
python -m uvicorn app.main:app --reload
```

Before using the workflow endpoints, make sure the configured database has tables. With PostgreSQL, run `alembic upgrade head` against your normal `DATABASE_URL`. For a temporary local check, use:

```powershell
$env:DATABASE_URL = "sqlite:///./phase03_manual_check.sqlite3"
alembic upgrade head
python -m uvicorn app.main:app --reload
```

Create a workflow run with cmd.exe style line continuations:

```sh
curl -X POST http://localhost:8000/api/workflow-runs ^
  -H "Content-Type: application/json" ^
  -d "{\"name\":\"sample invoice review\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":1250,\"invoice_id\":\"INV-1001\"}}"
```

PowerShell-friendly create example:

```powershell
$body = @{
  name = "sample invoice review"
  input_payload = @{
    vendor = "Acme"
    amount = 1250
    invoice_id = "INV-1001"
  }
} | ConvertTo-Json

Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/workflow-runs" `
  -ContentType "application/json" `
  -Body $body
```

List workflow runs:

```sh
curl http://localhost:8000/api/workflow-runs
```

Read workflow run by ID:

```sh
curl http://localhost:8000/api/workflow-runs/1
```

The created workflow run should show `status` as `created`, `risk_level` as `unknown`, `output_payload` as `null`, and `completed_at` as `null`.

## Common Errors And Fixes

If `ModuleNotFoundError: No module named 'app'` appears, run commands from the `backend` folder.

If the API cannot connect to PostgreSQL, check `DATABASE_URL` and confirm migrations have run with `alembic upgrade head`.

If `POST /api/workflow-runs` returns `422`, check that the JSON body includes a non-empty `name`.

If `GET /api/workflow-runs/999` returns `404`, that is expected when no workflow run exists with that ID.

If tests pass but manual API calls fail, remember that tests use isolated SQLite while the running app uses the configured `DATABASE_URL`.

## What We Now Understand

We now understand how a database model becomes an API resource.

The `WorkflowRun` table stores state. The Pydantic schemas define the API contract. The FastAPI router receives requests and sends responses. SQLAlchemy persists the data. Tests prove the behavior without relying on a local database server.

## Next Phase Preview

Phase 04 can build on this by adding the first execution behavior, such as a deterministic agent simulator or service layer depending on the phase plan.

Phase 03 stops here. No agent simulator logic, validation engine logic, approval flow, frontend code, or Docker work belongs in this phase.
