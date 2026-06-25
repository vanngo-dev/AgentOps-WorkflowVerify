# Frontend

The frontend is the React, TypeScript, and Vite browser app for the AgentOps Workflow Verification Platform.

It provides:

- workflow dashboard
- workflow creation form
- execute action
- workflow detail page
- input and output payload inspection
- agent step timeline
- validation results
- approval history
- approve and reject controls
- trace ID display when the backend includes one

## Configuration

The frontend reads `VITE_API_BASE_URL`.

Use this value for normal local development:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Create `frontend/.env` from `frontend/.env.example` only when you need to override the default.

## Run

```sh
npm install
npm run dev
```

Open:

```text
http://localhost:5173/workflow-runs
```

Workflow detail pages use:

```text
http://localhost:5173/workflow-runs/:id
```

## Test

```sh
npm test
npm run build
npm run playwright:install
npm run test:e2e
```

The Playwright config starts the backend and frontend test servers for the E2E suite.

## Run With Docker Compose

From the repository root:

```sh
docker compose up --build
```

Open:

```text
http://localhost:5173/workflow-runs
```

The Compose stack sets `VITE_API_BASE_URL=http://localhost:8000` so browser requests go to the backend port published on the host.
