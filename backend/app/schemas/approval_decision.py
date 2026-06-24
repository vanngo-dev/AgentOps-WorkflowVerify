from pydantic import BaseModel, Field


class ApprovalDecisionCreate(BaseModel):
    reviewer_name: str = Field(min_length=1, max_length=255)
    comment: str | None = None
