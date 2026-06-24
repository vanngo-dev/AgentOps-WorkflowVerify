# Phase 10 - End-To-End Testing

## What We Build In This Phase

In Phase 10, we add Playwright end-to-end tests for the browser-to-backend workflow.

We add:

- Playwright configuration in the frontend
- E2E scripts in `frontend/package.json`
- a clear `frontend/e2e/` test folder
- a low-risk workflow E2E test
- a high-risk approval workflow E2E test
- helper scripts that start the backend and frontend for E2E runs

We do not add Docker, GitHub Actions, real LLM calls, background workers, or frontend/backend redesign work.

## What E2E Tests Prove

End-to-end tests prove that the full user path works through the real browser, frontend, API client, backend routes, service layer, and database.

For this project, that means a user can create a workflow run, execute it, inspect the trace, and approve a high-risk workflow without mocking the application boundary.

## Unit, Integration, And E2E Tests

Unit tests check small pieces in isolation, such as React page behavior with mocked API functions.

Integration tests check connected backend behavior, such as FastAPI endpoints writing records and returning workflow detail.

E2E tests check the complete application path from browser action to backend state and back to the UI.

## Why E2E Tests Matter For Agent Workflows

Agent workflows are multi-step. A run can start as `created`, move through execution, collect agent steps, create validation results, require approval, and then finish with a human decision.

E2E tests prove those pieces still work together after individual screens and endpoints have already passed their narrower tests.

## How To Install Playwright

From the frontend folder:

```sh
cd frontend
npm install
npm run playwright:install
```

The install script installs the Chromium browser used by this phase.

## How To Run Backend And Frontend

For normal manual use, run the backend:

```sh
cd backend
python -m uvicorn app.main:app --reload
```

Run the frontend:

```sh
cd frontend
npm run dev
```

Open:

```text
http://localhost:5173/workflow-runs
```

The E2E test command starts its own backend and frontend servers. The backend uses SQLite at `backend/tmp/phase10_e2e.sqlite3`, which is local generated data and is not committed. The E2E frontend server builds the app and serves the compiled files at port `5173`.

## How To Run E2E Tests

From the frontend folder:

```sh
npm run test:e2e
```

For interactive debugging:

```sh
npm run test:e2e:ui
```

The frontend points to:

```text
VITE_API_BASE_URL=http://localhost:8000
```

The backend runs at:

```text
http://localhost:8000
```

The frontend runs at:

```text
http://localhost:5173
```

## Debugging Common Playwright Failures

If Playwright says the browser is missing, run `npm run playwright:install`.

If a web server times out, confirm ports `8000` and `5173` are free, then rerun `npm run test:e2e`.

If workflow creation fails, check the backend terminal output and confirm the SQLite migration completed.

If a locator fails, inspect the Playwright trace or run `npm run test:e2e:ui` to see the browser state.

If a test finds old workflows, that is expected. E2E tests use unique names and invoice IDs, so they do not require an empty database.

## Manual Verification

Low-risk workflow:

- Open `http://localhost:5173/workflow-runs`
- Create a workflow with vendor `Acme`, amount `500`, and a unique invoice ID
- Verify it appears with status `created` and risk level `unknown`
- Execute it
- Verify status becomes `completed` and risk level becomes `low`
- Open detail
- Verify input payload, output payload, agent steps, and validation results are visible
- Verify approve and reject controls are hidden

High-risk approval workflow:

- Create a workflow with vendor `Acme`, amount `7500`, and a unique invoice ID
- Execute it
- Verify status becomes `approval_required` and risk level becomes `high`
- Open detail
- Verify `high_amount_requires_review` is visible
- Enter reviewer name and comment
- Approve it
- Verify status becomes `approved`
- Verify approval history shows the approved decision
- Verify approve and reject controls are hidden

Optional rejection check:

- Create another high-risk workflow
- Execute it
- Reject it from detail
- Verify status becomes `rejected` and approval history shows the rejected decision

## What We Now Understand

The backend tests prove the API and workflow state rules. The frontend tests prove page behavior with mocked API calls. The E2E tests prove the real application path that an operator uses.

Together, they give the phase-gated project a stronger safety net without adding deployment tooling or real LLM complexity.

## Next Phase Preview

Phase 11 can build on the E2E foundation, but Phase 10 stops here.

Future work may add deployment, CI, real model calls, or richer operations tooling. Those remain outside this phase.
