# Phase 11 - Docker Compose Local Environment

## What We Build In This Phase

In Phase 11, we add a Docker Compose local environment for the AgentOps Workflow Verification Platform.

We add:

- root `docker-compose.yml`
- `backend/Dockerfile`
- `frontend/Dockerfile`
- Docker ignore files for backend and frontend build contexts
- Docker-friendly environment examples
- documentation for starting, stopping, resetting, and verifying the stack

We do not add GitHub Actions, real LLM calls, background workers, or frontend/backend redesign work.

## Containers

`postgres` runs the official PostgreSQL image and stores data in the named `postgres_data` volume.

`backend` builds the FastAPI app from `backend/Dockerfile`, runs Alembic migrations on startup, and serves the API on port `8000`.

`frontend` builds the React/Vite app image from `frontend/Dockerfile` and runs the Vite dev server on port `5173`.

## How Frontend Talks To Backend

The frontend uses `VITE_API_BASE_URL`.

In Compose, that value is:

```text
http://localhost:8000
```

That URL is browser-facing. The user browser runs on the host machine, so it must call the backend through the backend port published by Docker Compose.

## How Backend Talks To Postgres

The backend uses `DATABASE_URL`.

In Compose, that value points at the Compose service name:

```text
postgresql+psycopg://postgres:postgres@postgres:5432/agentops_workflow
```

Inside the Compose network, `postgres` resolves to the PostgreSQL container.

## Environment Variables

Root `.env.example` includes local defaults for:

- `DATABASE_URL`
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `VITE_API_BASE_URL`

Docker Compose also includes fallback defaults, so the stack can run without copying `.env.example`.

The backend still reads `DATABASE_URL` from the environment for non-Docker local development, and SQLite-based tests continue to override database setup inside tests.

## Start The Stack

From the repository root:

```sh
docker compose up --build
```

Open:

```text
http://localhost:5173/workflow-runs
```

## Stop The Stack

```sh
docker compose down
```

## Reset The Database Volume

This deletes the local Compose PostgreSQL data:

```sh
docker compose down -v
```

Then start again:

```sh
docker compose up --build
```

## Migrations

The backend container runs migrations on startup:

```sh
python -m alembic upgrade head
```

To run migrations manually:

```sh
docker compose exec backend python -m alembic upgrade head
```

## Logs

```sh
docker compose logs backend
docker compose logs frontend
docker compose logs postgres
```

## Verify Backend Health

```sh
curl http://localhost:8000/health
```

Expected response:

```json
{"status":"ok"}
```

## Verify Frontend Workflow

Open:

```text
http://localhost:5173/workflow-runs
```

Low-risk workflow:

- Create a workflow with vendor `Acme`, amount `500`, and a unique invoice ID
- Execute it
- Verify status becomes `completed`
- Verify risk level becomes `low`
- Open detail and verify trace plus validation results

High-risk workflow:

- Create a workflow with vendor `Acme`, amount `7500`, and a unique invoice ID
- Execute it
- Verify status becomes `approval_required`
- Verify risk level becomes `high`
- Open detail
- Approve it with reviewer name and comment
- Verify status becomes `approved`
- Verify approval history shows the approved decision

## Common Docker Errors And Fixes

If `docker compose` is not found, install Docker Desktop or use a Docker version that includes Compose v2.

If the daemon is not running, start Docker Desktop and retry.

If port `5432`, `8000`, or `5173` is already in use, stop the other local process or change the published port in `docker-compose.yml`.

If backend startup fails during migrations, check PostgreSQL logs:

```sh
docker compose logs postgres
docker compose logs backend
```

If the frontend loads but API calls fail, confirm `VITE_API_BASE_URL` points to `http://localhost:8000` and the backend health check works from the host.

If the database has old local data, reset the named volume:

```sh
docker compose down -v
```

## What We Now Understand

The project can still run through the local Python and npm workflows, and it now also has a one-command Compose environment for the main services.

Docker Compose gives the platform a repeatable local stack without adding CI, deployment automation, real LLM calls, or background workers.

## Next Phase Preview

Phase 12 can build on this local environment, but Phase 11 stops here.

Future work may add deployment automation, CI, or real model integrations. Those remain outside this phase.
