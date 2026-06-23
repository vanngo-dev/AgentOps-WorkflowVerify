from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class WorkflowRunCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    input_payload: dict[str, Any] | None = None


class WorkflowRunRead(BaseModel):
    id: int
    name: str
    status: str
    risk_level: str
    input_payload: dict[str, Any] | None
    output_payload: dict[str, Any] | None
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)
