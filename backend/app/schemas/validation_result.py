from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ValidationResultRead(BaseModel):
    id: int
    rule_name: str
    passed: bool
    severity: str
    message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
