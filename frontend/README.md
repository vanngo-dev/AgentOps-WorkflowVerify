# Frontend

This folder contains the React and TypeScript frontend for the AgentOps Workflow Verification Platform.

Phase 10 adds Playwright end-to-end tests on top of the workflow dashboard and detail viewer. The browser tests create workflows, execute them, inspect trace evidence, and approve a high-risk workflow against the live frontend and backend.

This phase does not add Docker, GitHub Actions, background workers, real LLM calls, or frontend/backend redesign work.

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
npm run playwright:install
npm run test:e2e
```
