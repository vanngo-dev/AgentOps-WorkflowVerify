# Phase 06 - Human Approval Flow

## What We Build In This Phase

In Phase 06, we add human-in-the-loop approval and rejection.

We add two endpoints:

- `POST /api/workflow-runs/{workflow_run_id}/approve`
- `POST /api/workflow-runs/{workflow_run_id}/reject`

These endpoints work only for workflows in `approval_required` status. We do not add frontend code, Docker, real LLM calls, or background workers in this phase.

## Why This Phase Matters

AI systems need human review when the action is too sensitive to complete automatically.

In this project, high-risk workflows are not failed. They are paused. The platform says, "This looks structurally valid, but a person needs to make the final call." That is the core idea behind human-in-the-loop AgentOps.

## Mental Model

Think of `approval_required` as a waiting room.

The simulated agent has already run. The validation engine has already checked the output. The workflow is valid, but it is high risk. Phase 06 gives a human reviewer two choices:

- approve the workflow
- reject the workflow

Either choice creates an audit record and finishes the workflow.

## Files Added Or Changed

Added:

- `backend/app/schemas/approval_decision.py`
- `backend/app/tests/test_human_approval_api.py`
- `docs/06-human-approval.md`

Changed:

- `Makefile`
- `README.md`
- `backend/README.md`
- `backend/app/api/workflow_runs.py`
- `backend/app/schemas/__init__.py`

## Step-By-Step Walkthrough

First, we add an approval request schema. The request accepts a reviewer name and an optional comment.

Next, we add the approve and reject routes to the workflow run API router.

Each route loads the workflow run, checks that it exists, and confirms the workflow is in `approval_required` status. If the workflow is missing, the API returns `404`. If the workflow is in any other status, the API returns `409`.

Then, the route creates an `ApprovalDecision` record. That record stores the workflow ID, decision, reviewer name, comment, and timestamp.

Finally, the workflow status becomes either `approved` or `rejected`, and `completed_at` is set.

## Key Code Concepts

`approval_required` means the workflow passed validation but needs a human decision before it can finish.

Only `approval_required` workflows can be approved or rejected because every other state already means something else. A completed workflow is already done. A failed workflow is not safe to approve. A created or running workflow is not ready for review.

Approval decisions create an audit trail. The platform can show who reviewed the workflow, what they decided, and what comment they left.

Duplicate approval or rejection is blocked because the first human decision is final in this phase. Once a workflow is `approved` or `rejected`, it is no longer waiting for review.

The status transitions are:

```text
created -> running -> completed
created -> running -> validation_failed
created -> running -> approval_required -> approved
created -> running -> approval_required -> rejected
```

Invalid transitions include:

```text
completed -> approved
completed -> rejected
approved -> rejected
rejected -> approved
approved -> approved
rejected -> rejected
```

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
$env:DATABASE_URL = "sqlite:///./phase06_manual_check.sqlite3"
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

Create a high-risk workflow:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs `
  -H "Content-Type: application/json" `
  -d "{\"name\":\"high risk invoice\",\"input_payload\":{\"vendor\":\"Acme\",\"amount\":7500,\"invoice_id\":\"INV-HIGH-1\"}}"
```

Execute workflow:

```sh
curl -X POST http://localhost:8000/api/workflow-runs/1/execute
```

Read workflow:

```sh
curl http://localhost:8000/api/workflow-runs/1
```

Expected:

- `status` is `approval_required`
- `risk_level` is `high`
- `completed_at` is `null`

Approve workflow:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs/1/approve `
  -H "Content-Type: application/json" `
  -d "{\"reviewer_name\":\"local reviewer\",\"comment\":\"Approved after review.\"}"
```

Read workflow again:

```sh
curl http://localhost:8000/api/workflow-runs/1
```

Expected:

- `status` is `approved`
- `completed_at` is not `null`
- an approval decision is stored

Duplicate approve check:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs/1/approve `
  -H "Content-Type: application/json" `
  -d "{\"reviewer_name\":\"local reviewer\",\"comment\":\"Trying duplicate approval.\"}"
```

Expected:

- `409 Conflict`

Reject flow:

Create another high-risk workflow, execute it, then reject it:

```powershell
curl -X POST http://localhost:8000/api/workflow-runs/2/reject `
  -H "Content-Type: application/json" `
  -d "{\"reviewer_name\":\"local reviewer\",\"comment\":\"Rejected after review.\"}"
```

Expected:

- `status` is `rejected`
- `completed_at` is not `null`
- an approval decision is stored

Invalid approval flow:

Create a low-risk workflow, execute it, then try to approve it.

Expected:

- low-risk workflow status is `completed`
- approval attempt returns `409 Conflict`

## Common Errors And Fixes

If approval returns `404`, check the workflow ID.

If approval or rejection returns `409`, the workflow is not in `approval_required` status.

If a high-risk workflow is still `created`, execute it before approving or rejecting it.

If a low-risk workflow cannot be approved, that is expected. Low-risk workflows complete automatically after validation.

If you do not see an approval decision in the API response, remember that Phase 06 stores the audit record in the database but keeps the workflow response focused on the workflow run.

## What We Now Understand

We now understand how human review fits into the workflow lifecycle.

The validation engine pauses high-risk workflows. The approval endpoints let a person finish them. The decision record creates an audit trail. Invalid transitions are blocked so the workflow history stays clean.

## Next Phase Preview

Phase 07 can build a frontend shell that lets users see workflow state and trigger these backend actions through a UI.

Phase 06 stops here. No frontend code, Docker, real LLM calls, or background workers belong in this phase.
