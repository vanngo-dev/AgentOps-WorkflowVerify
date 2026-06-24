# Frontend

This folder contains the React and TypeScript frontend for the AgentOps Workflow Verification Platform.

Phase 08 connects the Workflow Runs page to the FastAPI backend. The page can list workflow runs, create a new workflow run, execute runs that are still in `created` status, and show loading, empty, and error states.

This phase does not add workflow detail pages, trace viewing, approve/reject UI, Playwright, Docker, or real LLM calls.

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
```

## Test

```sh
npm test
npm run build
```
