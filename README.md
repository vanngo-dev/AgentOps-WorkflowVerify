# AgentOps Workflow Verification Platform

Welcome to the AgentOps Workflow Verification Platform. This repository is a phase-gated learning and build workflow for creating a platform that can test, validate, observe, and approve AI-agent behavior before it is trusted in real workflows.

This is not being built as a resume project. It is being built like a tutorial series: one clear phase at a time, with every phase documented, checked, committed, and stopped before the next phase begins.

## Project Purpose

AI agents can plan, call tools, make decisions, and affect business systems. That power is useful, but it also creates risk. The purpose of this project is to build a platform that helps teams answer questions like:

- Did the agent follow the workflow?
- Did it call the right tools in the right order?
- Did it handle errors safely?
- Did a human approve the step when approval was required?
- Can we see what happened after the run is complete?

The first version will use a deterministic simulated agent instead of a real LLM. That keeps the early phases focused on platform behavior, verification rules, data flow, and user experience before adding the complexity and cost of live model calls.

## Phase-Gated Workflow

This repository uses a strict phase-gated implementation process.

Each phase must be:

- implemented
- tested
- documented
- committed
- stopped

No phase may begin until the previous phase is complete. This keeps the project easy to teach, easy to review, and easy to rewind if a decision needs to change.

## Current Phase Status

Current phase: Phase 01 - Backend Foundation

Status: backend foundation added

This phase adds a minimal FastAPI backend with health endpoints, configuration, logging setup, and backend tests. It does not add database models, workflow execution, frontend code, Docker, real agents, or optional tools.

## How To Use This Repository

Start by reading:

- `docs/00-project-overview.md`
- `docs/01-backend-foundation.md`
- `docs/glossary.md`
- `backend/README.md`
- `frontend/README.md`

Use the placeholder Makefile commands to keep the workflow consistent:

```sh
make help
make test
make lint
make docs
```

In Phase 01, `make test` and `make lint` delegate to the backend test and lint commands.

## Phase Rule

Each phase must be tested, documented, committed, and stopped before moving forward.

That rule is part of the product. The same discipline this platform will eventually verify for AI-agent workflows is also used to build the platform itself.
