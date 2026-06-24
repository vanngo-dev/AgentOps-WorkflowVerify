# Frontend

This folder contains the React and TypeScript frontend for the AgentOps Workflow Verification Platform.

Phase 09 adds workflow detail and trace viewing on top of the workflow dashboard. Operators can open a run, inspect payloads, review agent steps and validation results, see approval history, and approve or reject workflows that are waiting for human review.

This phase does not add Playwright, Docker, GitHub Actions, background workers, real LLM calls, or observability infrastructure.

## Configuration

Create a local `.env` file from `.env.example` when the backend runs somewhere other than the default URL.

```sh
VITE_API_BASE_URL=http://localhost:8000
```

## Run

```sh
npm install
npm run dev
```

Open:

```text
http://localhost:5173/workflow-runs
http://localhost:5173/workflow-runs/1
```

## Test

```sh
npm test
npm run build
```
