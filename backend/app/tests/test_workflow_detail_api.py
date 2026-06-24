from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.request_context import TRACE_ID_HEADER
from app.db.base import Base
from app.db.session import get_db
from app.main import app


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
    amount: int = 500,
    invoice_id: str = "INV-LOW-1",
) -> dict[str, object]:
    response = client.post(
        "/api/workflow-runs",
        json={
            "name": "invoice review",
            "input_payload": {
                "vendor": "Acme",
                "amount": amount,
                "invoice_id": invoice_id,
            },
        },
    )

    assert response.status_code == 201
    return response.json()


def execute_workflow_run(
    client: TestClient,
    workflow_run_id: object,
) -> dict[str, object]:
    response = client.post(f"/api/workflow-runs/{workflow_run_id}/execute")

    assert response.status_code == 200
    return response.json()


def test_detail_endpoint_returns_workflow_summary(client: TestClient) -> None:
    workflow_run = create_workflow_run(client)

    response = client.get(f"/api/workflow-runs/{workflow_run['id']}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workflow_run["id"]
    assert data["name"] == "invoice review"
    assert data["status"] == "created"
    assert data["risk_level"] == "unknown"
    assert data["input_payload"] == {
        "vendor": "Acme",
        "amount": 500,
        "invoice_id": "INV-LOW-1",
    }
    assert data["output_payload"] is None
    assert data["agent_steps"] == []
    assert data["validation_results"] == []
    assert data["approval_decisions"] == []


def test_detail_endpoint_includes_trace_id(client: TestClient) -> None:
    workflow_run = create_workflow_run(client)

    response = client.get(
        f"/api/workflow-runs/{workflow_run['id']}",
        headers={TRACE_ID_HEADER: "phase-13-trace-id"},
    )

    assert response.status_code == 200
    assert response.json()["trace_id"] == "phase-13-trace-id"


def test_detail_endpoint_includes_agent_steps_after_execution(
    client: TestClient,
) -> None:
    workflow_run = create_workflow_run(client)
    execute_workflow_run(client, workflow_run["id"])

    response = client.get(f"/api/workflow-runs/{workflow_run['id']}")

    assert response.status_code == 200
    agent_steps = response.json()["agent_steps"]
    assert len(agent_steps) == 5
    assert agent_steps[0]["step_index"] == 1
    assert agent_steps[0]["step_name"] == "inspect_input"
    assert agent_steps[0]["status"] == "completed"
    assert agent_steps[0]["input_snapshot"] is not None
    assert agent_steps[0]["output_snapshot"] is not None


def test_detail_endpoint_includes_validation_results_after_execution(
    client: TestClient,
) -> None:
    workflow_run = create_workflow_run(client)
    execute_workflow_run(client, workflow_run["id"])

    response = client.get(f"/api/workflow-runs/{workflow_run['id']}")

    assert response.status_code == 200
    validation_results = response.json()["validation_results"]
    assert len(validation_results) == 5
    assert {result["rule_name"] for result in validation_results} >= {
        "required_vendor_present",
        "amount_is_positive",
    }


def test_detail_endpoint_includes_approval_decisions_after_approval(
    client: TestClient,
) -> None:
    workflow_run = create_workflow_run(
        client,
        amount=7500,
        invoice_id="INV-HIGH-1",
    )
    execute_workflow_run(client, workflow_run["id"])

    approval_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/approve",
        json={
            "reviewer_name": "local reviewer",
            "comment": "Approved high amount invoice.",
        },
    )
    response = client.get(f"/api/workflow-runs/{workflow_run['id']}")

    assert approval_response.status_code == 200
    assert response.status_code == 200
    decisions = response.json()["approval_decisions"]
    assert len(decisions) == 1
    assert decisions[0]["decision"] == "approved"
    assert decisions[0]["reviewer_name"] == "local reviewer"
    assert decisions[0]["comment"] == "Approved high amount invoice."


def test_detail_endpoint_includes_approval_decisions_after_rejection(
    client: TestClient,
) -> None:
    workflow_run = create_workflow_run(
        client,
        amount=7500,
        invoice_id="INV-HIGH-2",
    )
    execute_workflow_run(client, workflow_run["id"])

    rejection_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/reject",
        json={
            "reviewer_name": "local reviewer",
            "comment": "Rejected high amount invoice.",
        },
    )
    response = client.get(f"/api/workflow-runs/{workflow_run['id']}")

    assert rejection_response.status_code == 200
    assert response.status_code == 200
    decisions = response.json()["approval_decisions"]
    assert len(decisions) == 1
    assert decisions[0]["decision"] == "rejected"
    assert decisions[0]["reviewer_name"] == "local reviewer"
    assert decisions[0]["comment"] == "Rejected high amount invoice."


def test_detail_endpoint_returns_404_for_missing_workflow(client: TestClient) -> None:
    response = client.get("/api/workflow-runs/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Workflow run not found."}
