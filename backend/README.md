# Backend

This folder contains the Phase 01 FastAPI backend foundation.

Phase 01 creates the smallest useful backend: an app entry point, health endpoints, configuration, logging setup, and tests. It does not create database models, workflow execution, real agents, queues, or approval logic yet.

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
    tests/
      test_health.py
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
