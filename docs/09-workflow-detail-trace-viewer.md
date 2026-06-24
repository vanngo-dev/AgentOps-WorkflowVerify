# Phase 09 - Workflow Detail And Trace Viewer

## What We Build In This Phase

In Phase 09, we add a workflow detail page and trace viewer.

We add:

- a backend detail response for `GET /api/workflow-runs/{workflow_run_id}`
- detail schemas for agent steps, validation results, and approval decisions
- a frontend route at `/workflow-runs/:id`
- dashboard links from workflow names to their detail pages
- a `WorkflowRunDetailPage` that shows summary fields, payloads, agent steps, validation results, and approval history
- approve and reject controls for workflows in `approval_required` status
- backend and frontend tests for the detail and approval-review flow

We do not add Playwright, Docker, GitHub Actions, background workers, real LLM calls, or observability infrastructure.

## Why Traces Matter

A workflow status is useful, but it is not enough by itself.

When a run is completed, failed, or waiting for approval, the operator needs to see the evidence behind that state. The trace shows the workflow record, the payloads that moved through the system, the simulated agent steps, the validation rules, and any human decisions. That makes the run explainable instead of only labeled.

## How Agent Steps Explain Behavior

Agent steps show the timeline of execution. Each step includes its index, name, status, input snapshot, output snapshot, and error message when one exists.

That lets a reviewer answer practical questions:

- What did the agent inspect?
- What did each step produce?
- Did the expected steps run in order?
- Was any step blocked or failed?

In this phase, the agent is still deterministic, so the trace is stable and testable.

## Why Validation Results Are Visible

Validation results explain why a run became `completed`, `validation_failed`, or `approval_required`.

Each result shows the rule name, pass/fail result, severity, message, and creation time. For example, an invalid invoice can show which required field failed, while a high amount can show the `high_amount_requires_review` warning that caused human review.

## Approval History

Approval history creates an audit trail for human decisions.

When a reviewer approves or rejects a high-risk workflow, the decision, reviewer name, comment, and timestamp are stored and shown on the detail page. After that decision, the workflow leaves `approval_required`, receives a terminal status, and the approve/reject controls disappear.

## Approve And Reject State Rules

Approve and reject actions are available only for workflows in `approval_required` status.

Allowed paths:

```text
created -> running -> approval_required -> approved
created -> running -> approval_required -> rejected
```

Blocked paths:

```text
completed -> approved
completed -> rejected
validation_failed -> approved
validation_failed -> rejected
approved -> rejected
rejected -> approved
```

The backend keeps these rules in the approval endpoints. The frontend follows the same rule by rendering the controls only when the workflow status is `approval_required`.

## Files Added Or Changed

Added:

- `backend/app/schemas/agent_step.py`
- `backend/app/schemas/validation_result.py`
- `backend/app/tests/test_workflow_detail_api.py`
- `frontend/src/pages/WorkflowRunDetailPage.tsx`
- `frontend/src/tests/WorkflowRunDetailPage.test.tsx`
- `docs/09-workflow-detail-trace-viewer.md`

Changed:

- `.gitignore`
- `Makefile`
- `README.md`
- `backend/README.md`
- `backend/app/api/workflow_runs.py`
- `backend/app/models/workflow_run.py`
- `backend/app/schemas/__init__.py`
- `backend/app/schemas/approval_decision.py`
- `backend/app/schemas/workflow_run.py`
- `frontend/README.md`
- `frontend/src/App.tsx`
- `frontend/src/api/workflowRuns.ts`
- `frontend/src/pages/WorkflowRunsPage.tsx`
- `frontend/src/styles.css`
- `frontend/src/tests/App.test.tsx`
- `frontend/src/tests/WorkflowRunsPage.test.tsx`

## How To Run It

Start the backend:

```sh
cd backend
python -m uvicorn app.main:app --reload
```

Start the frontend:

```sh
cd frontend
npm install
npm run dev
```

Open:

```text
http://localhost:5173/workflow-runs
```

Then select a workflow name to open its detail page.

## How To Test It

Run backend checks:

```sh
cd backend
python -m pytest
python -m ruff check .
```

Run frontend checks:

```sh
cd frontend
npm test
npm run build
```

## Manual Verification

Low-risk workflow:

- Create a workflow with amount `500`
- Execute it
- Open the detail page
- Verify status is `completed`
- Verify risk level is `low`
- Verify input payload, output payload, agent steps, and validation results are visible
- Verify approve and reject controls are hidden

High-risk approval workflow:

- Create a workflow with amount `7500`
- Execute it
- Open the detail page
- Verify status is `approval_required`
- Verify risk level is `high`
- Verify `high_amount_requires_review` is visible in validation results
- Verify approve and reject controls are visible
- Approve it
- Verify status is `approved`
- Verify `completed_at` is set
- Verify approval history shows the approved decision
- Verify approve and reject controls are hidden

High-risk rejection workflow:

- Create another workflow with amount `7500`
- Execute it
- Open the detail page
- Reject it
- Verify status is `rejected`
- Verify approval history shows the rejected decision
- Verify approve and reject controls are hidden

Invalid workflow:

- Create a workflow with a missing vendor or negative amount
- Execute it
- Open the detail page
- Verify status is `validation_failed`
- Verify validation results explain the failed rules
- Verify approve and reject controls are hidden

## Common Errors And Fixes

If the detail page shows a loading or network error, confirm the backend is running at the configured `VITE_API_BASE_URL`.

If a detail page returns `404`, confirm the workflow ID exists.

If approve or reject returns `409`, the workflow is not in `approval_required` status.

If no agent steps or validation results appear, execute the workflow before opening the detail page.

If frontend requests fail because of CORS, confirm the backend allows the Vite origin.

## What We Now Understand

The dashboard shows the list of runs. The detail page explains one run.

Together, they give the operator a path from status overview to workflow evidence. The backend remains the system of record, and the frontend asks for fresh detail after every approval or rejection so the screen reflects the real workflow state.

## Next Phase Preview

Phase 10 can build on the detail and trace viewer, but Phase 09 stops here.

Future work may add broader operational workflows, stronger review screens, or deployment tooling. Playwright, Docker, GitHub Actions, background workers, real LLM calls, and observability infrastructure remain outside this phase.
