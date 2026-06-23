from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import AgentStep, ValidationResult, WorkflowRun
from app.services.agent_simulator import SIMULATED_STEP_NAMES


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


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def create_workflow_run(
    client: TestClient,
    input_payload: dict[str, object] | None = None,
) -> dict[str, object]:
    if input_payload is None:
        input_payload = {
            "vendor": "Acme Supplies",
            "amount": 1250,
            "invoice_id": "INV-1001",
        }

    response = client.post(
        "/api/workflow-runs",
        json={
            "name": "sample invoice review",
            "input_payload": input_payload,
        },
    )

    assert response.status_code == 201
    return response.json()


def test_execute_workflow_run_success(
    client: TestClient,
    db_session: Session,
) -> None:
    created = create_workflow_run(client)

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["risk_level"] == "medium"
    assert data["completed_at"] is not None
    assert data["output_payload"] == {
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

    steps = list(
        db_session.scalars(
            select(AgentStep)
            .where(AgentStep.workflow_run_id == created["id"])
            .order_by(AgentStep.step_index),
        ).all(),
    )
    assert len(steps) == 5
    assert [step.step_name for step in steps] == list(SIMULATED_STEP_NAMES)

    validation_results = list(
        db_session.scalars(
            select(ValidationResult).where(
                ValidationResult.workflow_run_id == created["id"],
            ),
        ).all(),
    )
    assert len(validation_results) == 5


def test_execute_low_risk_workflow_completes(client: TestClient) -> None:
    created = create_workflow_run(
        client,
        {
            "vendor": "Acme Supplies",
            "amount": 500,
            "invoice_id": "INV-LOW-1",
        },
    )

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["risk_level"] == "low"
    assert response.json()["completed_at"] is not None


def test_execute_high_risk_workflow_requires_approval(client: TestClient) -> None:
    created = create_workflow_run(
        client,
        {
            "vendor": "Acme Supplies",
            "amount": 7500,
            "invoice_id": "INV-HIGH-1",
        },
    )

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    assert response.json()["status"] == "approval_required"
    assert response.json()["risk_level"] == "high"
    assert response.json()["completed_at"] is None


def test_execute_missing_vendor_fails_validation(client: TestClient) -> None:
    created = create_workflow_run(
        client,
        {
            "amount": 500,
            "invoice_id": "INV-MISSING-VENDOR",
        },
    )

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    assert response.json()["status"] == "validation_failed"
    assert response.json()["risk_level"] == "low"
    assert response.json()["completed_at"] is not None


def test_execute_missing_invoice_id_fails_validation(client: TestClient) -> None:
    created = create_workflow_run(
        client,
        {
            "vendor": "Acme Supplies",
            "amount": 500,
        },
    )

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    assert response.json()["status"] == "validation_failed"


def test_execute_negative_amount_fails_validation(client: TestClient) -> None:
    created = create_workflow_run(
        client,
        {
            "vendor": "Acme Supplies",
            "amount": -50,
            "invoice_id": "INV-NEGATIVE",
        },
    )

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    assert response.json()["status"] == "validation_failed"
    assert response.json()["risk_level"] == "unknown"


def test_execute_missing_amount_fails_validation(client: TestClient) -> None:
    created = create_workflow_run(
        client,
        {
            "vendor": "Acme Supplies",
            "invoice_id": "INV-MISSING-AMOUNT",
        },
    )

    response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert response.status_code == 200
    assert response.json()["status"] == "validation_failed"
    assert response.json()["risk_level"] == "unknown"


def test_execute_unknown_workflow_run_returns_404(client: TestClient) -> None:
    response = client.post("/api/workflow-runs/999/execute")

    assert response.status_code == 404


def test_repeated_execution_returns_409(client: TestClient) -> None:
    created = create_workflow_run(client)

    first_response = client.post(f"/api/workflow-runs/{created['id']}/execute")
    second_response = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_non_created_workflow_run_cannot_be_executed(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = WorkflowRun(
        name="already running workflow",
        status="running",
        input_payload={"invoice_id": "INV-2002"},
    )
    db_session.add(workflow_run)
    db_session.commit()
    db_session.refresh(workflow_run)

    response = client.post(f"/api/workflow-runs/{workflow_run.id}/execute")

    assert response.status_code == 409
