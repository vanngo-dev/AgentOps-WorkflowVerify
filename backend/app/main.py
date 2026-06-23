from fastapi import FastAPI

from app.api.health import router as health_router
from app.api.workflow_runs import router as workflow_runs_router
from app.core.config import get_settings
from app.core.logging import configure_logging

settings = get_settings()
configure_logging(settings)

app = FastAPI(title=settings.app_name)
app.include_router(health_router)
app.include_router(workflow_runs_router)
