from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import AgentStep, WorkflowRun
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


def create_workflow_run(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/api/workflow-runs",
        json={
            "name": "sample invoice review",
            "input_payload": {
                "vendor": "Acme Supplies",
                "amount": 1250,
                "invoice_id": "INV-1001",
            },
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
    assert data["risk_level"] == "unknown"
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
