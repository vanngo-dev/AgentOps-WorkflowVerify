from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ApprovalDecisionCreate(BaseModel):
    reviewer_name: str = Field(min_length=1, max_length=255)
    comment: str | None = None


class ApprovalDecisionRead(BaseModel):
    id: int
    decision: str
    reviewer_name: str | None
    comment: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
