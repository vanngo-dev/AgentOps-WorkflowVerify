# Final Verification Checklist

Use this checklist before treating the AgentOps Workflow Verification Platform as complete on a machine or branch.

Do not mark Docker, E2E, or GitHub Actions as passed unless they actually ran and passed.

## Environment Prerequisites

- Python 3.12 is available.
- Backend dependencies are installed with `python -m pip install -e .`.
- Node and npm are available.
- Frontend dependencies are installed with `npm install` or `npm ci`.
- Docker Desktop or a compatible Docker Engine is running if Docker checks are required.
- Ports `5432`, `8000`, and `5173` are available for local stack checks.
- Playwright Chromium is installed with `npm run playwright:install` if needed.

## Backend Verification Checklist

Run:

```sh
cd backend
python -m pytest
python -m ruff check .
```

Confirm:

- health tests pass
- model tests pass
- workflow API tests pass
- execution tests pass
- validation tests pass
- approval tests pass
- detail API tests pass
- request ID middleware tests pass
- Ruff reports no lint errors

## Frontend Verification Checklist

Run:

```sh
cd frontend
npm test
npm run build
```

Confirm:

- app tests pass
- workflow dashboard tests pass
- workflow detail tests pass
- trace ID rendering test passes
- TypeScript build passes
- Vite build succeeds

## E2E Verification Checklist

Run if Playwright is configured and practical:

```sh
cd frontend
npm run test:e2e
```

Confirm:

- low-risk workflow E2E test passes
- high-risk approval E2E test passes
- Playwright starts the backend and frontend servers
- failures are investigated instead of hidden by loosening assertions

## Docker Verification Checklist

Validate Compose configuration:

```sh
docker compose config
```

If Docker is available, run:

```sh
docker compose up --build
```

Confirm:

- `postgres` becomes healthy
- `backend` starts and runs migrations
- `frontend` starts on port `5173`
- `curl http://localhost:8000/health` returns `{"status":"ok"}`
- `http://localhost:5173/workflow-runs` loads in the browser

Stop the stack:

```sh
docker compose down
```

Reset local Docker data only when needed:

```sh
docker compose down -v
```

## CI Verification Checklist

After pushing to GitHub, confirm the Actions run passes.

Jobs to check:

- Backend
- Frontend
- Playwright E2E
- Docker Compose Config

Do not claim GitHub Actions passed until GitHub shows the workflow completed successfully.

## Observability Verification Checklist

Run the backend, then check generated request IDs:

```sh
curl -i http://localhost:8000/health
```

Confirm:

- response includes `X-Request-ID`
- value is non-empty

Check provided request IDs:

```sh
curl -i http://localhost:8000/health -H "X-Request-ID: final-check-123"
```

Confirm:

- response includes `X-Request-ID: final-check-123`

Execute a workflow and confirm logs include:

- `event=workflow_created`
- `event=workflow_execution_start`
- `event=agent_step_created`
- `event=agent_step_completed`
- `event=validation_summary`
- `event=validation_status`
- `event=approval_decision_recorded` for approval/rejection flows
- `trace_id`
- `workflow_run_id`

## Manual Workflow Scenario 1: Low-Risk Completed

1. Open `http://localhost:5173/workflow-runs`.
2. Create a workflow:
   - vendor: `Acme`
   - amount: `500`
   - invoice ID: unique value
3. Confirm the dashboard shows:
   - status `created`
   - risk level `unknown`
4. Execute the workflow.
5. Confirm:
   - status `completed`
   - risk level `low`
6. Open detail.
7. Confirm:
   - input payload is visible
   - output payload is visible
   - agent steps are visible
   - validation results are visible
   - approve/reject controls are hidden

## Manual Workflow Scenario 2: High-Risk Approval

1. Create a workflow:
   - vendor: `Acme`
   - amount: `7500`
   - invoice ID: unique value
2. Execute the workflow.
3. Confirm:
   - status `approval_required`
   - risk level `high`
4. Open detail.
5. Confirm `high_amount_requires_review` is visible.
6. Enter reviewer name and comment.
7. Approve the workflow.
8. Confirm:
   - status `approved`
   - approval history shows an approved decision
   - approve/reject controls are hidden

## Manual Workflow Scenario 3: High-Risk Rejection

1. Create another high-risk workflow:
   - vendor: `Acme`
   - amount: `7500`
   - invoice ID: unique value
2. Execute the workflow.
3. Confirm:
   - status `approval_required`
   - risk level `high`
4. Open detail.
5. Enter reviewer name and comment.
6. Reject the workflow.
7. Confirm:
   - status `rejected`
   - approval history shows a rejected decision
   - approve/reject controls are hidden

## Manual Workflow Scenario 4: Invalid Input

1. Create an invalid workflow, such as:
   - missing vendor, or
   - negative amount
2. Execute the workflow.
3. Confirm:
   - status `validation_failed`
   - validation results explain the failed rule
   - workflow has terminal completion timestamp

## Final Release Readiness Checklist

- README explains how to understand, run, test, and extend the project.
- Phase docs exist through Phase 14.
- Architecture review is complete.
- Final verification checklist is complete.
- Backend tests pass.
- Backend lint passes.
- Frontend tests pass.
- Frontend build passes.
- E2E tests pass or the reason they could not run is documented.
- Docker Compose config validates.
- Docker stack runs or the reason it could not run is documented.
- CI is configured.
- GitHub Actions status is checked after push.
- Observability headers and logs are verified.
- No real LLM calls were added.
- No background workers were added.
- No production infrastructure was added.
