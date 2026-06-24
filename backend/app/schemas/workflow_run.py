from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.agent_step import AgentStepRead
from app.schemas.approval_decision import ApprovalDecisionRead
from app.schemas.validation_result import ValidationResultRead


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


class WorkflowRunDetailRead(WorkflowRunRead):
    agent_steps: list[AgentStepRead]
    validation_results: list[ValidationResultRead]
    approval_decisions: list[ApprovalDecisionRead]
