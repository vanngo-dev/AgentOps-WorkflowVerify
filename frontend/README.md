# Frontend

This folder contains the React and TypeScript frontend for the AgentOps Workflow Verification Platform.

Phase 11 adds a Dockerfile used by the root Compose stack. The frontend still supports the local npm workflow and can also run in Docker against the backend at `http://localhost:8000`.

This phase does not add GitHub Actions, background workers, real LLM calls, or frontend/backend redesign work.

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

## Run With Docker Compose

From the repository root:

```sh
docker compose up --build
```

Open:

```text
http://localhost:5173/workflow-runs
```

The Compose stack sets `VITE_API_BASE_URL=http://localhost:8000` so browser requests go to the published backend port.
