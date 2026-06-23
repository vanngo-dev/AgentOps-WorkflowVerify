# Backend Foundation

This is Phase 01 of the AgentOps Workflow Verification Platform. In the tutorial story, Phase 00 gave us the empty workshop. Phase 01 puts the first real tool on the bench: a tiny FastAPI backend that can start, answer health checks, and prove itself with tests.

## What We Build In This Phase

In this phase, we build the backend foundation only.

We add:

- a FastAPI app entry point
- a health router
- a configuration module
- a logging module
- backend tests
- backend Python project metadata
- Makefile commands for backend checks

We do not add database models, workflow models, frontend code, Docker, real agents, or optional tools.

## Why This Phase Matters

Before we can verify an AI-agent workflow, we need a backend that can be started, imported, tested, and trusted as a stable foundation.

FastAPI gives us the web API layer. Pytest gives us repeatable checks. Ruff gives us a basic code-quality gate. Health endpoints give people and automation a quick way to ask, "Is this service alive?" and "Is this service ready to receive traffic?"

That may sound small, but it is the first real platform habit: every phase should leave behind something that can be checked.

## Mental Model

Think of the backend like a small control room.

The app entry point turns the control room on. The router decides which requests go where. The config module reads settings. The logging module controls how messages are written. The tests walk up to the control room door and make sure the basic signals work.

For now, the only signals are:

- `/health` means the app process is alive
- `/ready` means the app is ready to serve requests

Later phases can make readiness smarter, but Phase 01 keeps it intentionally simple.

## Files Added Or Changed

Added:

- `backend/pyproject.toml`
- `backend/app/main.py`
- `backend/app/api/health.py`
- `backend/app/core/config.py`
- `backend/app/core/logging.py`
- `backend/app/tests/test_health.py`
- `docs/01-backend-foundation.md`

Changed:

- `README.md`
- `Makefile`
- `backend/README.md`

## Step-By-Step Walkthrough

First, we create `backend/pyproject.toml`. This file declares the backend as a Python 3.12 project and lists the packages this phase needs: FastAPI, Uvicorn, Pytest, HTTPX, Pydantic Settings, and Ruff.

Next, we create `backend/app/main.py`. This is the import path Uvicorn will use when it runs `app.main:app`. It creates the FastAPI application and attaches the health router.

Then, we create `backend/app/api/health.py`. This file owns two routes:

- `GET /health` returns `{"status": "ok"}`
- `GET /ready` returns `{"status": "ready"}`

After that, we add `backend/app/core/config.py`. This gives the app a clear place for settings instead of scattering environment reads throughout the code.

Then, we add `backend/app/core/logging.py`. This gives the app a clear place to configure logging as the backend grows.

Finally, we add `backend/app/tests/test_health.py`. These tests import the app and call the health endpoints using FastAPI's test client.

## Key Code Concepts

FastAPI is the Python web framework that turns Python functions into HTTP API endpoints. In this phase, it lets us define a small backend without writing low-level server code.

Uvicorn is the local ASGI server. It runs the FastAPI app during development.

Pydantic Settings gives us a typed settings object. In later phases, this will matter more as configuration grows.

Health endpoints matter because services need simple operational signals. Humans, scripts, load balancers, and deployment systems all need a quick way to check service state.

`/health` and `/ready` are separate because they answer different questions. `/health` says the process is alive. `/ready` says the service is ready to handle requests. A service can be alive before it is ready, especially once databases, queues, migrations, or external dependencies are added.

App structure means files have clear jobs. API routes live under `app/api`. shared backend helpers live under `app/core`. Tests live under `app/tests`. The goal is to make the next file obvious before we create it.

Pytest verifies the backend by importing the app, making in-memory requests to the endpoints, and checking the response status codes and JSON bodies.

## How To Run It

From the backend folder:

```sh
uvicorn app.main:app --reload
```

Then open another terminal and run:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected responses:

```json
{"status":"ok"}
{"status":"ready"}
```

## How To Test It

From the backend folder:

```sh
pytest
```

If Ruff is installed, run:

```sh
ruff check .
```

On Windows, if `pytest` or `ruff` is installed but the command is not on your PATH, run the same tools through Python:

```sh
python -m pytest
python -m ruff check .
```

From the repository root, the Makefile delegates to the same backend commands:

```sh
make test
make lint
```

## Manual Verification

Use these commands for a hands-on check:

```sh
cd backend
uvicorn app.main:app --reload
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected curl responses:

```json
{"status":"ok"}
{"status":"ready"}
```

## Common Errors And Fixes

If `uvicorn` is not found, install the backend dependencies for this project environment.

If `ModuleNotFoundError: No module named 'app'` appears, make sure you are running commands from the `backend` folder.

If `pytest` cannot import FastAPI, make sure the dependencies from `backend/pyproject.toml` are installed in the active Python environment.

If `/health` works but `/ready` does not, check that `app.include_router(health_router)` is present in `backend/app/main.py`.

If Ruff reports import sorting issues, run the lint command again after organizing imports in the reported file.

## What We Now Understand

We now understand how the backend starts, where API routes live, where configuration belongs, where logging setup belongs, and how tests prove the smallest backend behavior.

The key win is not the two JSON responses. The key win is that the repository now has a real backend quality gate.

## Next Phase Preview

The next phase can build on this foundation, but Phase 01 stops here.

Future work may add the first domain concepts for workflow verification, such as workflow definitions or simulated run structures. Those belong to the next phase, not this one.
