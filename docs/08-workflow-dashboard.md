# Phase 08 - Workflow Dashboard

## What We Build In This Phase

In Phase 08, we turn the frontend shell into a real workflow dashboard.

We add:

- backend CORS support for the Vite frontend
- a frontend API client for workflow runs
- workflow run listing
- loading, empty, and error states
- a create workflow run form
- an execute button for runs in `created` status
- frontend tests with mocked API functions

We do not build workflow detail pages, trace viewing, approve/reject UI, Playwright, Docker, or real LLM calls.

## Why This Phase Matters

The backend can already create and execute workflow runs. The frontend now needs to show that state to an operator.

This phase is where the platform starts to feel connected. A person can create a workflow run, see its status, execute it, and watch the state change.

That is the first dashboard loop: create, observe, act, refresh.

## Mental Model

Think of the backend as the system of record and the frontend as the operator console.

The backend owns workflow state. The frontend asks for that state through API calls. When the operator creates or executes a run, the frontend sends the request and then reloads the list.

The page does not guess what happened. It asks the backend again.

## Files Added Or Changed

Added:

- `frontend/.env.example`
- `frontend/src/api/workflowRuns.ts`
- `frontend/src/tests/WorkflowRunsPage.test.tsx`
- `docs/08-workflow-dashboard.md`

Changed:

- `.gitignore`
- `Makefile`
- `README.md`
- `backend/app/core/config.py`
- `backend/app/main.py`
- `backend/app/tests/test_health.py`
- `frontend/README.md`
- `frontend/package.json`
- `frontend/scripts/run-vite-build.mjs`
- `frontend/scripts/run-vite-dev.mjs`
- `frontend/scripts/run-vitest.mjs`
- `frontend/src/api/client.ts`
- `frontend/src/pages/WorkflowRunsPage.tsx`
- `frontend/src/styles.css`
- `frontend/src/tests/App.test.tsx`
- `frontend/tsconfig.json`

## Step-By-Step Walkthrough

First, we add CORS to the backend. CORS allows the browser app at `http://localhost:5173` to call the API at `http://localhost:8000`.

Next, we update the frontend API client. The base URL comes from `VITE_API_BASE_URL`, and if that value is not set, it defaults to `http://localhost:8000`.

Then, we add workflow-specific API functions:

- `listWorkflowRuns()`
- `createWorkflowRun()`
- `executeWorkflowRun(workflowRunId)`

After that, we replace the placeholder Workflow Runs page with a dashboard. It loads workflow runs, shows a table, displays status and risk level, and includes a create form.

Finally, we add tests that mock the API functions. The tests prove the page behavior without requiring a live backend.

## Key Code Concepts

The frontend talks to the backend with `fetch`. The generic `requestJson()` helper handles the base URL, JSON headers, response parsing, and error messages.

CORS is needed because the frontend and backend run on different local origins. The browser treats `localhost:5173` and `localhost:8000` as different origins, even though both are on the same machine.

An API client function is a small wrapper around one backend endpoint. Instead of scattering URLs across components, the page calls clear functions like `listWorkflowRuns()`.

Loading, empty, and error states make the dashboard understandable. Loading means the request is still in flight. Empty means the backend returned an empty list. Error means the request failed.

The create form maps UI fields into the backend payload:

```json
{
  "name": "sample invoice review",
  "input_payload": {
    "vendor": "Acme",
    "amount": 1250,
    "invoice_id": "INV-1001"
  }
}
```

Only `created` workflows show Execute because later statuses have already moved forward in the workflow. A completed, failed, approval-required, approved, or rejected run should not be executed again from this page.

Status and risk level visibility matter because operators need a fast way to see which workflow runs are finished, blocked, risky, or waiting for approval.

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

## How To Test It

Run frontend tests:

```sh
cd frontend
npm test
```

Run the frontend build:

```sh
cd frontend
npm run build
```

Run backend checks:

```sh
cd backend
python -m pytest
python -m ruff check .
```

## Manual Verification

Manual scenario 1:

- Open `http://localhost:5173/workflow-runs`
- If no workflows exist, verify the empty state appears

Manual scenario 2:

- Create a low-risk workflow
- Use name `low risk invoice`
- Use vendor `Acme`
- Use amount `500`
- Use invoice ID `INV-LOW-1`
- Verify the list shows `status: created` and `risk_level: unknown`
- Click Execute
- Verify the list updates to `status: completed` and `risk_level: low`

Manual scenario 3:

- Create a high-risk workflow
- Use name `high risk invoice`
- Use vendor `Acme`
- Use amount `7500`
- Use invoice ID `INV-HIGH-1`
- Click Execute
- Verify the list updates to `status: approval_required` and `risk_level: high`

Manual scenario 4:

- Create an invalid workflow
- Use name `invalid invoice`
- Leave vendor empty if desired
- Use amount `-50`
- Use invoice ID `INV-BAD-1`
- Click Execute
- Verify the list updates to `status: validation_failed`

## Common Errors And Fixes

If the frontend cannot reach the backend, confirm the backend is running on `http://localhost:8000`.

If the browser reports a CORS error, confirm the backend includes `http://localhost:5173` in its allowed origins.

If the page stays in loading state, check the browser network panel and the backend terminal.

If create fails, check that the form sends a `name` and an `input_payload` object with `vendor`, `amount`, and `invoice_id`.

If Execute does not appear, check the workflow status. The button only appears when status is `created`.

## What We Now Understand

We now understand how the frontend and backend work together.

The backend stores workflow state. The frontend asks for that state, displays it, and sends create or execute requests. Tests keep the dashboard behavior stable without needing a real backend during frontend unit tests.

## Next Phase Preview

Phase 09 can add the workflow detail page and trace viewer. That is where the platform can show agent steps, validation results, and deeper workflow evidence.

Phase 08 stops here. No workflow detail page, trace viewer, approve/reject UI, Playwright, Docker, or real LLM work belongs in this phase.
