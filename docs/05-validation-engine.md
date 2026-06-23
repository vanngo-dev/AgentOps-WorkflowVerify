# Phase 05 - Validation Engine

## What We Build In This Phase

In Phase 05, we add a deterministic validation engine that runs after the simulated agent finishes its five steps.

The validation engine does four jobs:

- checks the agent output with fixed rules
- stores `ValidationResult` records
- assigns a workflow `risk_level`
- chooses the final workflow status

The rules are:

- `required_vendor_present`
- `required_invoice_id_present`
- `amount_is_positive`
- `decision_is_valid`
- `high_amount_requires_review`

We do not add human approval endpoints, frontend code, Docker, real LLM calls, or background workers in this phase.

## Why This Phase Matters

Agent output should not flow directly into the rest of a system just because it looks useful.

Even our simulator can produce an output for incomplete or unsafe input. A real AI agent can do even more surprising things. Validation gives the platform a deterministic checkpoint after execution. It asks, "Does this output satisfy the rules we already know?"

That is safer than trusting agent output directly. The rules are predictable, testable, and easy to audit.

## Mental Model

Think of the agent simulator as the worker and the validation engine as the inspector.

The worker produces an output. The inspector checks the output against known rules. Each rule creates a record. The workflow status is decided from those records and the risk level.

The status transitions are:

- `created` when the workflow run is first created
- `running` while the simulator is executing
- `completed` when validation passes and risk is low or medium
- `approval_required` when validation passes but risk is high
- `validation_failed` when any error-level rule fails

High-risk workflows do not become completed in this phase. They wait for the human approval flow that comes later.

## Files Added Or Changed

Added:

- `backend/app/services/validation_engine.py`
- `backend/app/tests/test_validation_engine.py`
- `docs/05-validation-engine.md`

Changed:

- `Makefile`
- `README.md`
- `backend/README.md`
- `backend/app/services/__init__.py`
- `backend/app/services/agent_simulator.py`
- `backend/app/tests/test_agent_simulator.py`
- `backend/app/tests/test_workflow_execution_api.py`

## Step-By-Step Walkthrough

First, we add `backend/app/services/validation_engine.py`. This file contains deterministic rules and risk logic.

Next, we update the simulator. After it produces `output_payload`, it calls the validation engine before committing the final workflow state.

Then, the validation engine stores five `ValidationResult` records. Each record has a rule name, pass/fail value, severity, and message.

After that, the engine assigns risk:

- amount below `1000` is `low`
- amount from `1000` up to `4999.99` is `medium`
- amount `5000` or greater is `high`
- missing, invalid, zero, or negative amounts are `unknown`

Finally, the engine chooses the workflow status. Error-level failures become `validation_failed`. High-risk valid workflows become `approval_required`. Low and medium valid workflows become `completed`.

## Key Code Concepts

Deterministic validation rules are simple Python checks. They are intentionally boring in the best way: same input, same result, every time.

`ValidationResult` records create an audit trail. Later, when someone asks why a workflow failed or why it needs approval, the platform can show the exact rule results.

Risk level is separate from validation success. A high-risk invoice can pass validation and still require human review.

`completed_at` is set only for terminal statuses in this phase:

- `completed`
- `validation_failed`

For `approval_required`, `completed_at` stays `null` because the workflow is waiting for a person.

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
$env:DATABASE_URL = "sqlite:///./phase05_manual_check.sqlite3"
alembic upgrade head
python -m uvicorn app.main:app --reload
```

## How To Test It

From the backend folder:

```sh
python -m pytest
python -m ruff check .
```

The tests use isolated SQLite databases. They do not depend on local PostgreSQL.

## Manual Verification

Start the backend:

```sh
python -m uvicorn app.main:app --reload
```

Low-risk workflow:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"low risk invoice\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":500,\"invoice_id\":\"INV-LOW-1\"}}"

curl -X POST http://localhost:8000/api/workflow-runs/1/execute

curl http://localhost:8000/api/workflow-runs/1
```

Expected:

- `status` is `completed`
- `risk_level` is `low`
- `output_payload` exists

High-risk workflow:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"high risk invoice\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":7500,\"invoice_id\":\"INV-HIGH-1\"}}"

curl -X POST http://localhost:8000/api/workflow-runs/2/execute

curl http://localhost:8000/api/workflow-runs/2
```

Expected:

- `status` is `approval_required`
- `risk_level` is `high`
- `completed_at` is `null`

Invalid workflow:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"invalid invoice\",\"input_payload\":{\"amount\":-50,\"invoice_id\":\"INV-BAD-1\"}}"

curl -X POST http://localhost:8000/api/workflow-runs/3/execute

curl http://localhost:8000/api/workflow-runs/3
```

Expected:

- `status` is `validation_failed`
- `risk_level` is safely assigned, usually `unknown` for invalid amounts
- validation results are stored in the database and covered by tests

## Common Errors And Fixes

If a workflow stays `created`, make sure you called the `/execute` endpoint.

If a high-risk workflow is not `completed`, that is expected. High risk now waits for human approval in a later phase.

If a workflow returns `validation_failed`, inspect the input payload. Missing vendor, missing invoice ID, invalid amount, or invalid decision output will fail error-level validation.

If repeated execution returns `409`, that is expected. Only workflows in `created` status can be executed.

If the running API cannot connect to the database, check `DATABASE_URL` and run `alembic upgrade head`.

## What We Now Understand

We now understand how agent output becomes verifiable platform state.

The simulator creates a trace and output. The validation engine checks that output. Validation results explain what passed or failed. Risk level decides whether a valid workflow can finish or must wait for approval.

## Next Phase Preview

Phase 06 can add the human approval flow for workflows in `approval_required` status.

Phase 05 stops here. No human approval endpoints, frontend code, Docker, real LLM calls, or background workers belong in this phase.
