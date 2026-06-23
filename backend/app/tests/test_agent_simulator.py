from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import AgentStep, WorkflowRun
from app.services.agent_simulator import SIMULATED_STEP_NAMES, execute_workflow_run


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False)

    with session_factory() as session:
        yield session

    Base.metadata.drop_all(engine)


def create_workflow_run(db_session: Session) -> WorkflowRun:
    workflow_run = WorkflowRun(
        name="sample invoice review",
        input_payload={
            "vendor": "Acme Supplies",
            "amount": 1250,
            "invoice_id": "INV-1001",
        },
    )
    db_session.add(workflow_run)
    db_session.commit()
    db_session.refresh(workflow_run)

    return workflow_run


def test_agent_simulator_completes_workflow_run(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session)

    executed_run = execute_workflow_run(db_session, workflow_run)

    assert executed_run.status == "completed"
    assert executed_run.completed_at is not None
    assert executed_run.output_payload == {
        "decision": "approve",
        "reason": (
            "Amount is within standard threshold and required fields are present."
        ),
        "extracted": {
            "vendor": "Acme Supplies",
            "amount": 1250,
            "invoice_id": "INV-1001",
        },
    }


def test_agent_simulator_creates_five_ordered_steps(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session)

    execute_workflow_run(db_session, workflow_run)

    steps = list(
        db_session.scalars(
            select(AgentStep)
            .where(AgentStep.workflow_run_id == workflow_run.id)
            .order_by(AgentStep.step_index),
        ).all(),
    )

    assert len(steps) == 5
    assert [step.step_name for step in steps] == list(SIMULATED_STEP_NAMES)
    assert [step.step_index for step in steps] == [1, 2, 3, 4, 5]
    assert all(step.status == "completed" for step in steps)
    assert all(step.started_at is not None for step in steps)
    assert all(step.completed_at is not None for step in steps)
    assert all(step.error_message is None for step in steps)
