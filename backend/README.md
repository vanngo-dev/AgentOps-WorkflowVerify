# Backend

This folder contains the FastAPI backend foundation and Phase 02 database model layer.

Phase 02 adds SQLAlchemy models, database session setup, Alembic migrations, and SQLite-backed model tests. It does not create workflow API endpoints, workflow execution, real agents, queues, approval workflows, or frontend code yet.

## Structure

```text
backend/
  app/
    main.py
    api/
      health.py
    core/
      config.py
      logging.py
    db/
      base.py
      session.py
    models/
      workflow_run.py
      agent_step.py
      validation_result.py
      approval_decision.py
    tests/
      test_health.py
      test_models.py
  alembic/
  pyproject.toml
  README.md
```

## Run Locally

Install the backend dependencies in your Python environment, then run:

```sh
uvicorn app.main:app --reload
```

Check the health endpoints:

```sh
curl http://localhost:8000/health
curl http://localhost:8000/ready
```

Expected responses:

```json
{"status":"ok"}
{"status":"ready"}
```

## Test

From this folder:

```sh
pytest
ruff check .
```

If those console scripts are not on your PATH, use:

```sh
python -m pytest
python -m ruff check .
```

## Database Migrations

Set `DATABASE_URL` to a PostgreSQL database URL for normal development:

```sh
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/agentops_workflow
```

Then run:

```sh
alembic upgrade head
```

If the console script is not on your PATH, run the Alembic executable from your active environment, such as:

```sh
.\.venv\Scripts\alembic.exe upgrade head
```

The model tests use SQLite so they can run without a local PostgreSQL server.
