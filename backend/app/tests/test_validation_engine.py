from collections.abc import Generator

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.models import ValidationResult, WorkflowRun
from app.services.validation_engine import validate_workflow_run


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


def create_workflow_run(
    db_session: Session,
    output_payload: dict[str, object],
) -> WorkflowRun:
    workflow_run = WorkflowRun(
        name="validation target",
        status="running",
        input_payload={},
        output_payload=output_payload,
    )
    db_session.add(workflow_run)
    db_session.commit()
    db_session.refresh(workflow_run)

    return workflow_run


def invoice_output(
    amount: object,
    vendor: object = "Acme Supplies",
    invoice_id: object = "INV-1001",
    decision: object = "approve",
) -> dict[str, object]:
    return {
        "decision": decision,
        "reason": "Simulated decision.",
        "extracted": {
            "vendor": vendor,
            "amount": amount,
            "invoice_id": invoice_id,
        },
    }


def test_valid_low_risk_workflow_completes(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session, invoice_output(amount=500))

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "completed"
    assert workflow_run.status == "completed"
    assert workflow_run.risk_level == "low"


def test_valid_medium_risk_workflow_completes(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session, invoice_output(amount=1250))

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "completed"
    assert workflow_run.status == "completed"
    assert workflow_run.risk_level == "medium"


def test_high_risk_workflow_requires_approval(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session, invoice_output(amount=7500))

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "approval_required"
    assert workflow_run.status == "approval_required"
    assert workflow_run.risk_level == "high"


def test_missing_vendor_causes_validation_failed(db_session: Session) -> None:
    workflow_run = create_workflow_run(
        db_session,
        invoice_output(amount=500, vendor=None),
    )

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "validation_failed"
    assert workflow_run.status == "validation_failed"


def test_missing_invoice_id_causes_validation_failed(db_session: Session) -> None:
    workflow_run = create_workflow_run(
        db_session,
        invoice_output(amount=500, invoice_id=""),
    )

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "validation_failed"
    assert workflow_run.status == "validation_failed"


def test_negative_amount_causes_validation_failed(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session, invoice_output(amount=-50))

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "validation_failed"
    assert workflow_run.risk_level == "unknown"


def test_invalid_amount_causes_validation_failed(db_session: Session) -> None:
    workflow_run = create_workflow_run(
        db_session,
        invoice_output(amount="not-a-number"),
    )

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "validation_failed"
    assert workflow_run.risk_level == "unknown"


def test_invalid_decision_causes_validation_failed(db_session: Session) -> None:
    workflow_run = create_workflow_run(
        db_session,
        invoice_output(amount=500, decision="maybe"),
    )

    status = validate_workflow_run(db_session, workflow_run)

    assert status == "validation_failed"


def test_validation_results_are_stored_with_rule_fields(db_session: Session) -> None:
    workflow_run = create_workflow_run(db_session, invoice_output(amount=7500))

    validate_workflow_run(db_session, workflow_run)
    db_session.commit()

    results = list(
        db_session.scalars(
            select(ValidationResult)
            .where(ValidationResult.workflow_run_id == workflow_run.id)
            .order_by(ValidationResult.id),
        ).all(),
    )

    assert len(results) == 5
    assert {result.rule_name for result in results} == {
        "required_vendor_present",
        "required_invoice_id_present",
        "amount_is_positive",
        "decision_is_valid",
        "high_amount_requires_review",
    }
    assert all(isinstance(result.passed, bool) for result in results)
    assert {result.severity for result in results}.issubset(
        {"info", "warning", "error"},
    )
    assert all(result.message for result in results)

    review_result = next(
        result
        for result in results
        if result.rule_name == "high_amount_requires_review"
    )
    assert review_result.passed is False
    assert review_result.severity == "warning"
