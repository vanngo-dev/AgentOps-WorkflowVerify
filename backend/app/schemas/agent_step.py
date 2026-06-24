from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class AgentStepRead(BaseModel):
    id: int
    step_index: int
    step_name: str
    input_snapshot: dict[str, Any] | None
    output_snapshot: dict[str, Any] | None
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    error_message: str | None

    model_config = ConfigDict(from_attributes=True)
