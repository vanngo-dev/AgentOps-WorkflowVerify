.RECIPEPREFIX := >

.PHONY: help test lint docs

help:
> @echo "AgentOps Workflow Verification Platform"
> @echo ""
> @echo "Available commands:"
> @echo "  make help  - Show this command list"
> @echo "  make test  - Run backend tests"
> @echo "  make lint  - Run backend lint checks"
> @echo "  make docs  - Show documentation entry points"

test:
> cd backend && python -m pytest

lint:
> cd backend && python -m ruff check .

docs:
> @echo "Read docs/00-project-overview.md"
> @echo "Read docs/01-backend-foundation.md"
> @echo "Read docs/02-database-model.md"
> @echo "Read docs/03-workflow-api.md"
> @echo "Read docs/04-agent-simulator.md"
> @echo "Read docs/05-validation-engine.md"
> @echo "Read docs/06-human-approval.md"
> @echo "Read docs/07-frontend-shell.md"
> @echo "Read docs/08-workflow-dashboard.md"
> @echo "Read docs/09-workflow-detail-trace-viewer.md"
> @echo "Read docs/10-e2e-tests.md"
> @echo "Read docs/11-docker-compose.md"
> @echo "Read docs/glossary.md"
