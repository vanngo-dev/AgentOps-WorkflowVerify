from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.agent_step import AgentStep
    from app.models.approval_decision import ApprovalDecision
    from app.models.validation_result import ValidationResult


def utc_now() -> datetime:
    return datetime.now(UTC)


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="created", nullable=False)
    risk_level: Mapped[str] = mapped_column(
        String(50),
        default="unknown",
        nullable=False,
    )
    input_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    output_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    agent_steps: Mapped[list[AgentStep]] = relationship(
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        order_by="AgentStep.step_index",
    )
    validation_results: Mapped[list[ValidationResult]] = relationship(
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        order_by="ValidationResult.id",
    )
    approval_decisions: Mapped[list[ApprovalDecision]] = relationship(
        back_populates="workflow_run",
        cascade="all, delete-orphan",
        order_by="ApprovalDecision.id",
    )
