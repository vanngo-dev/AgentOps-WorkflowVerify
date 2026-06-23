# Phase 04 - Agent Simulator

## What We Build In This Phase

In Phase 04, we add a deterministic simulated agent.

The simulator executes an existing workflow run through five named steps:

- `inspect_input`
- `classify_document`
- `extract_fields`
- `calculate_risk`
- `produce_decision`

We also add an API endpoint:

```text
POST /api/workflow-runs/{workflow_run_id}/execute
```

This phase does not add real LLM calls, LangGraph, validation engine logic, approval flow, frontend code, or Docker.

## Why This Phase Matters

The whole point of this project is to build the platform around agent behavior before trusting a real agent.

Real LLM output can vary from run to run. That is useful later, but it makes early platform development noisy. A deterministic simulator gives us stable behavior. The same input creates the same steps, the same output, and the same state transitions every time.

That lets us test workflow execution without debugging prompts, model settings, rate limits, or network calls.

## Mental Model

Think of the simulator like a training actor on a stage.

It is not the final AI agent. It is a predictable stand-in that walks through the same places the real agent will eventually walk through. Every step leaves a trace in the database.

The workflow starts as `created`. When execution begins, it becomes `running`. When the five simulated steps finish, it becomes `completed`.

## Files Added Or Changed

Added:

- `backend/app/services/agent_simulator.py`
- `backend/app/services/__init__.py`
- `backend/app/tests/test_agent_simulator.py`
- `backend/app/tests/test_workflow_execution_api.py`
- `docs/04-agent-simulator.md`

Changed:

- `Makefile`
- `README.md`
- `backend/README.md`
- `backend/app/api/workflow_runs.py`

## Step-By-Step Walkthrough

First, we create `backend/app/services/agent_simulator.py`. This file contains the deterministic execution logic.

Next, we update the workflow run API router. The new route loads the workflow run by ID, checks that it exists, checks that it is still in `created` status, and then calls the simulator.

Then, the simulator sets the workflow to `running`, creates five `AgentStep` records, stores the final `output_payload`, and marks the workflow as `completed`.

Finally, we add tests for the service and the API endpoint. The tests use isolated SQLite databases, so they do not depend on local PostgreSQL.

## Key Code Concepts

Deterministic simulation means the same input always produces the same output. That is why this phase uses plain Python logic instead of a real LLM.

An agent step is one named part of a workflow execution. Each step records an input snapshot, an output snapshot, a status, timestamps, and any error message. In this phase, every simulated step completes successfully.

AgentStep records form a trace. The trace is the history of what happened during execution. Later, validation and observability features can inspect this trace.

The `output_payload` is the final workflow result. For the sample invoice input, the simulator produces:

```json
{
  "decision": "approve",
  "reason": "Amount is within standard threshold and required fields are present.",
  "extracted": {
    "vendor": "Acme Supplies",
    "amount": 1250,
    "invoice_id": "INV-1001"
  }
}
```

Repeated execution is blocked because a completed workflow already has a trace and an output. Running it again would mix old and new history. For now, a workflow can only be executed from `created` status.

## How To Run It

From the backend folder:

```sh
python -m uvicorn app.main:app --reload
```

Make sure the configured database has been migrated:

```sh
alembic upgrade head
```

If PostgreSQL is not running locally and you only want to try the API, use a temporary SQLite database:

```powershell
$env:DATABASE_URL = "sqlite:///./phase04_manual_check.sqlite3"
alembic upgrade head
python -m uvicorn app.main:app --reload
```

## How To Test It

From the backend folder:

```sh
python -m pytest
python -m ruff check .
```

The tests use isolated SQLite databases and do not depend on local PostgreSQL.

## Manual Verification

Start the backend:

```sh
python -m uvicorn app.main:app --reload
```

Create a workflow run:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"sample invoice review\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":1250,\"invoice_id\":\"INV-1001\"}}"
```

Execute the workflow run:

```sh
curl -X POST http://localhost:8000/api/workflow-runs/1/execute
```

Read the workflow run:

```sh
curl http://localhost:8000/api/workflow-runs/1
```

Expected result:

- `status` should be `completed`
- `output_payload` should be populated
- `completed_at` should not be `null`

Verify repeated execution:

```sh
curl -X POST http://localhost:8000/api/workflow-runs/1/execute
```

Expected result:

- `409 Conflict`

## Common Errors And Fixes

If `POST /api/workflow-runs/1/execute` returns `404`, create the workflow run first or check the ID.

If execution returns `409`, the workflow run is not in `created` status. A completed or running workflow cannot be executed again.

If the API cannot connect to PostgreSQL, check `DATABASE_URL` and run `alembic upgrade head` against a reachable database.

If tests pass but manual API calls fail, remember that tests use isolated SQLite while the running app uses your configured database.

If no `AgentStep` rows appear after execution, confirm that the execute endpoint is being called and that the workflow was still in `created` status.

## What We Now Understand

We now understand how the platform records a deterministic workflow execution.

The workflow run stores the overall state. Agent steps store the trace. The simulator produces a stable output payload. The API blocks repeat execution so the trace stays clean.

## Next Phase Preview

Phase 05 can add validation engine logic that inspects workflow outputs and step traces.

Phase 04 stops here. No validation engine, approval flow, frontend code, Docker, real LLM calls, or external agent framework work belongs in this phase.
