# Phase 12 - GitHub Actions CI

## What We Build In This Phase

In Phase 12, we add GitHub Actions continuous integration.

CI runs the same core quality gates used locally whenever code is pushed or a pull request is opened.

We add:

- `.github/workflows/ci.yml`
- a backend CI job
- a frontend CI job
- a Playwright E2E CI job
- a Docker Compose config validation job

We do not add observability, trace IDs, real LLM calls, background workers, new app features, or deployment automation.

## What CI Is

Continuous integration is an automated check that runs after code changes leave the local machine.

Instead of relying only on a developer remembering every command, GitHub Actions runs the expected test and build commands in a clean environment.

## Why CI Matters For Phase-Gated Development

This project is built one phase at a time.

CI helps enforce that discipline by proving each committed phase still passes the backend, frontend, E2E, and Compose configuration checks before more work builds on top of it.

## Triggers

The workflow runs on:

- `push`
- `pull_request`

## Backend Job

The backend job runs on `ubuntu-latest` with Python `3.12`.

Commands:

```sh
cd backend
python -m pip install --upgrade pip
python -m pip install -e .
python -m pytest
python -m ruff check .
```

The job uses pip caching keyed from `backend/pyproject.toml`.

## Frontend Job

The frontend job runs on `ubuntu-latest` with Node `24`.

Commands:

```sh
cd frontend
npm ci
npm test
npm run build
```

The job uses npm caching keyed from `frontend/package-lock.json`.

## E2E Job

Playwright E2E runs in CI.

The job installs backend dependencies, frontend dependencies, and Chromium, then runs:

```sh
cd frontend
npm run test:e2e
```

The existing Playwright config starts the SQLite-backed backend and built frontend test server. The job sets:

```text
VITE_API_BASE_URL=http://localhost:8000
```

If this job becomes flaky in GitHub-hosted runners, inspect the Playwright failure output first. Do not hide flaky behavior by loosening assertions; fix the unstable cause.

## Docker Compose Config Job

The Compose job validates configuration only:

```sh
docker compose config
```

It does not run `docker compose up` in CI in this phase.

## Reading Failed CI Logs

Open the failed GitHub Actions run, select the failed job, and expand the failed step.

Useful places to look:

- backend install errors in `Install backend dependencies`
- backend failures in `Run backend tests`
- lint failures in `Run backend lint`
- frontend dependency errors in `Install frontend dependencies`
- React or TypeScript issues in `Run frontend build`
- browser workflow failures in `Run Playwright E2E tests`
- Compose syntax or environment mistakes in `Validate Docker Compose config`

## Common CI Failures And Fixes

If backend tests cannot import a dependency, check `backend/pyproject.toml` and rerun `python -m pip install -e .` locally.

If frontend install fails, confirm `frontend/package-lock.json` is committed and matches `frontend/package.json`.

If Playwright cannot find a browser, check the `Install Playwright browser` step.

If E2E server startup times out, inspect the backend startup logs and frontend build logs in the E2E job.

If Docker Compose validation fails, run `docker compose config` locally from the repository root.

## Push And Confirm GitHub Actions

After committing, push the branch:

```sh
git push
```

Then open the repository on GitHub and check the Actions tab.

Do not treat CI as passed until GitHub shows the workflow completed successfully.

## Local Verification

Before pushing, run:

```sh
cd backend
python -m pytest
python -m ruff check .
```

```sh
cd frontend
npm test
npm run build
npm run test:e2e
```

From the repository root:

```sh
docker compose config
```

## What We Now Understand

Local checks protect the current machine. CI protects the shared branch.

Phase 12 gives future phases an automated safety gate without adding deployment, observability, real LLM calls, or background execution.

## Next Phase Preview

Phase 13 can build on CI, but Phase 12 stops here.

Future work may add richer operational tooling, deployment automation, or real model integrations. Those remain outside this phase.
