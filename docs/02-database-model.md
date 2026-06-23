# Database Model

This is Phase 02 of the AgentOps Workflow Verification Platform. In the build series, Phase 01 gave us a backend that can start and answer health checks. Phase 02 gives that backend memory.

We are not building workflow APIs yet. We are not running an agent yet. We are not adding a frontend. We are only creating the database foundation that later phases will stand on.

## What We Build In This Phase

In this phase, we add:

- SQLAlchemy 2.x setup
- database session configuration
- Alembic migration setup
- the first workflow data models
- SQLite-backed model tests
- an initial migration for the workflow tables

The first tables are:

- `workflow_runs`
- `agent_steps`
- `validation_results`
- `approval_decisions`

## Why This Phase Matters

Workflow systems need persistent state because a workflow is not just one request and one response.

An agent workflow may start, pause, wait for a tool, fail validation, require approval, resume later, and then complete. If that history only lives in memory, it disappears when the process restarts. A verification platform needs to keep the record so people can inspect what happened.

That record is also what makes testing, validation, observability, and human approval real. The platform needs somewhere to store the workflow run, the agent steps, the validation results, and the human decisions.

## Mental Model

Think of a workflow run as the folder for one complete attempt.

Inside that folder, we keep:

- agent steps, which show what the agent did
- validation results, which show what rules passed or failed
- approval decisions, which show what humans allowed or rejected

The `WorkflowRun` is the parent record. The other records belong to it.

## Files Added Or Changed

Added:

- `backend/app/db/base.py`
- `backend/app/db/session.py`
- `backend/app/models/workflow_run.py`
- `backend/app/models/agent_step.py`
- `backend/app/models/validation_result.py`
- `backend/app/models/approval_decision.py`
- `backend/app/models/__init__.py`
- `backend/app/tests/test_models.py`
- `backend/alembic.ini`
- `backend/alembic/env.py`
- `backend/alembic/script.py.mako`
- `backend/alembic/versions/20260623_0001_create_workflow_tables.py`
- `docs/02-database-model.md`

Changed:

- `.env.example`
- `.gitignore`
- `README.md`
- `backend/README.md`
- `backend/app/core/config.py`
- `backend/pyproject.toml`

## Step-By-Step Walkthrough

First, we add SQLAlchemy and Alembic to `backend/pyproject.toml`. SQLAlchemy is the ORM that lets Python classes map to database tables. Alembic is the migration tool that changes the database schema over time.

Next, we create `backend/app/db/base.py`. This file defines the shared SQLAlchemy `Base`. Every model inherits from this base so SQLAlchemy can collect the full table map.

Then, we create `backend/app/db/session.py`. This file creates the database engine and session factory. Later API endpoints will use sessions when they need to read or write data.

After that, we create the four model files. Each model is one table:

- `WorkflowRun` stores the main workflow attempt
- `AgentStep` stores each step connected to a workflow run
- `ValidationResult` stores rule checks for a workflow run
- `ApprovalDecision` stores human review decisions for a workflow run

Then, we configure Alembic in `backend/alembic.ini` and `backend/alembic/env.py`. The important part is that Alembic imports the model metadata, which means migrations can understand the tables our models describe.

Finally, we add tests that create the tables in SQLite, insert a workflow run, attach child records, and query the relationships back from the parent.

## Key Code Concepts

SQLAlchemy models are Python classes that map to database tables. A class attribute like `name` maps to a table column. A relationship like `WorkflowRun.agent_steps` maps to the idea that one workflow run can have many agent step records.

Alembic migrations are versioned database changes. The first migration creates the four workflow tables. Later migrations will add or change tables without forcing every developer to rebuild the database by hand.

PostgreSQL is the normal development target because it is a production-grade relational database and supports the kind of structured workflow data this platform will need. The models use simple column types that are PostgreSQL-compatible.

SQLite is used for tests because it is fast, isolated, and does not require a local database server. The tests are not trying to prove PostgreSQL itself works. They are proving that our SQLAlchemy mappings, table creation, inserts, and relationships work.

String fields are used for `status`, `risk_level`, `decision`, and `severity` for now. Enums may be useful later, but this phase keeps the data model easy to read.

## How To Run It

For normal development, configure a PostgreSQL database URL:

```sh
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/agentops_workflow
```

Then run migrations from the backend folder:

```sh
cd backend
alembic upgrade head
```

If `alembic` is installed but not on your PATH, run the Alembic executable from your active environment. On Windows, that may look like:

```sh
.\.venv\Scripts\alembic.exe upgrade head
```

## How To Test It

From the backend folder:

```sh
pytest
```

If the console script is not on your PATH, use:

```sh
python -m pytest
```

Run lint:

```sh
ruff check .
```

Or:

```sh
python -m ruff check .
```

## Manual Verification

Use these commands for the Phase 02 check:

```sh
cd backend
pytest
ruff check .
alembic upgrade head
```

If PostgreSQL is not running or `DATABASE_URL` is not set to a reachable database, the Alembic command will not complete against PostgreSQL. That is expected for a machine without the database configured. The setup is still ready for PostgreSQL once `DATABASE_URL` points to a running database.

For a quick migration mechanics check without PostgreSQL, you can run Alembic against a temporary SQLite URL:

```sh
DATABASE_URL=sqlite:///./phase02_migration_check.sqlite3 alembic upgrade head
```

## Common Errors And Fixes

If `ModuleNotFoundError: No module named 'sqlalchemy'` appears, install the backend dependencies from `backend/pyproject.toml`.

If `alembic` is not recognized, activate the backend Python environment or run the Alembic executable from that environment, such as `.\.venv\Scripts\alembic.exe upgrade head` on Windows.

If PostgreSQL refuses the connection, confirm the server is running, the database exists, and `DATABASE_URL` has the right username, password, host, port, and database name.

If tests pass but PostgreSQL migrations fail, remember that the tests use SQLite on purpose. That proves the model mappings and relationships, not the local PostgreSQL service.

If Alembic cannot find the models, check that `backend/alembic/env.py` imports `app.models` and uses `Base.metadata`.

## What We Now Understand

We now understand how the backend stores workflow state.

A workflow run is the parent. Agent steps, validation results, and approval decisions are child records. SQLAlchemy describes that shape in Python. Alembic turns that shape into database schema changes. Pytest proves the model layer can create tables, insert records, and query relationships.

That is the foundation we need before building workflow APIs.

## Next Phase Preview

The next phase can start using these models from API or service code, depending on the phase plan.

Phase 02 stops here. No workflow endpoints, agent simulator logic, frontend code, or Docker work belongs in this phase.
