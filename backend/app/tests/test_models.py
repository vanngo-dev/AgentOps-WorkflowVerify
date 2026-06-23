from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, inspect, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import AgentStep, ApprovalDecision, ValidationResult, WorkflowRun


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


def test_models_can_be_imported() -> None:
    assert WorkflowRun.__tablename__ == "workflow_runs"
    assert AgentStep.__tablename__ == "agent_steps"
    assert ValidationResult.__tablename__ == "validation_results"
    assert ApprovalDecision.__tablename__ == "approval_decisions"


def test_tables_can_be_created_in_isolated_database(db_session: Session) -> None:
    table_names = set(inspect(db_session.bind).get_table_names())

    assert {
        "workflow_runs",
        "agent_steps",
        "validation_results",
        "approval_decisions",
    }.issubset(table_names)


def test_workflow_run_can_be_inserted(db_session: Session) -> None:
    workflow_run = WorkflowRun(
        name="Support request review",
        input_payload={"ticket_id": "TICKET-100"},
    )

    db_session.add(workflow_run)
    db_session.commit()
    db_session.refresh(workflow_run)

    assert workflow_run.id is not None
    assert workflow_run.status == "created"
    assert workflow_run.risk_level == "unknown"


def test_workflow_relationships_can_be_queried(db_session: Session) -> None:
    workflow_run = WorkflowRun(
        name="High-risk support workflow",
        input_payload={"customer_tier": "enterprise"},
    )
    workflow_run.agent_steps.append(
        AgentStep(
            step_index=1,
            step_name="Classify request",
            input_snapshot={"body": "Please update billing contact."},
            output_snapshot={"category": "billing"},
            status="completed",
        ),
    )
    workflow_run.validation_results.append(
        ValidationResult(
            rule_name="requires_human_approval",
            passed=True,
            severity="warning",
            message="Billing changes require review.",
        ),
    )
    workflow_run.approval_decisions.append(
        ApprovalDecision(
            decision="approved",
            reviewer_name="Casey Reviewer",
            comment="Looks safe for the simulated run.",
        ),
    )

    db_session.add(workflow_run)
    db_session.commit()

    stored_run = db_session.scalars(
        select(WorkflowRun).where(WorkflowRun.id == workflow_run.id),
    ).one()

    assert len(stored_run.agent_steps) == 1
    assert stored_run.agent_steps[0].step_name == "Classify request"
    assert stored_run.agent_steps[0].workflow_run_id == stored_run.id
    assert len(stored_run.validation_results) == 1
    assert stored_run.validation_results[0].rule_name == "requires_human_approval"
    assert stored_run.validation_results[0].workflow_run_id == stored_run.id
    assert len(stored_run.approval_decisions) == 1
    assert stored_run.approval_decisions[0].decision == "approved"
    assert stored_run.approval_decisions[0].workflow_run_id == stored_run.id
