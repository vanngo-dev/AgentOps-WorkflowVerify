from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import ApprovalDecision


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
    amount: int,
    invoice_id: str,
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


def create_executed_high_risk_workflow(client: TestClient) -> dict[str, object]:
    created = create_workflow_run(
        client=client,
        amount=7500,
        invoice_id="INV-HIGH-1",
    )

    executed = client.post(f"/api/workflow-runs/{created['id']}/execute")

    assert executed.status_code == 200
    assert executed.json()["status"] == "approval_required"
    return executed.json()


def approval_body(comment: str = "Reviewed high amount invoice.") -> dict[str, str]:
    return {
        "reviewer_name": "local reviewer",
        "comment": comment,
    }


def get_approval_decisions(
    db_session: Session,
    workflow_run_id: int,
) -> list[ApprovalDecision]:
    return list(
        db_session.scalars(
            select(ApprovalDecision).where(
                ApprovalDecision.workflow_run_id == workflow_run_id,
            ),
        ).all(),
    )


def test_high_risk_workflow_can_be_approved(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = create_executed_high_risk_workflow(client)

    response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/approve",
        json=approval_body("Approved after review."),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["completed_at"] is not None

    decisions = get_approval_decisions(db_session, int(workflow_run["id"]))
    assert len(decisions) == 1
    assert decisions[0].decision == "approved"
    assert decisions[0].reviewer_name == "local reviewer"
    assert decisions[0].comment == "Approved after review."


def test_high_risk_workflow_can_be_rejected(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = create_executed_high_risk_workflow(client)

    response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/reject",
        json=approval_body("Rejected after review."),
    )

    assert response.status_code == 200
    assert response.json()["status"] == "rejected"
    assert response.json()["completed_at"] is not None

    decisions = get_approval_decisions(db_session, int(workflow_run["id"]))
    assert len(decisions) == 1
    assert decisions[0].decision == "rejected"
    assert decisions[0].reviewer_name == "local reviewer"
    assert decisions[0].comment == "Rejected after review."


def test_cannot_approve_completed_low_risk_workflow(client: TestClient) -> None:
    created = create_workflow_run(
        client=client,
        amount=500,
        invoice_id="INV-LOW-1",
    )
    executed = client.post(f"/api/workflow-runs/{created['id']}/execute")

    response = client.post(
        f"/api/workflow-runs/{created['id']}/approve",
        json=approval_body(),
    )

    assert executed.status_code == 200
    assert executed.json()["status"] == "completed"
    assert response.status_code == 409


def test_cannot_reject_completed_low_risk_workflow(client: TestClient) -> None:
    created = create_workflow_run(
        client=client,
        amount=500,
        invoice_id="INV-LOW-2",
    )
    executed = client.post(f"/api/workflow-runs/{created['id']}/execute")

    response = client.post(
        f"/api/workflow-runs/{created['id']}/reject",
        json=approval_body(),
    )

    assert executed.status_code == 200
    assert executed.json()["status"] == "completed"
    assert response.status_code == 409


def test_cannot_approve_missing_workflow(client: TestClient) -> None:
    response = client.post("/api/workflow-runs/999/approve", json=approval_body())

    assert response.status_code == 404


def test_cannot_reject_missing_workflow(client: TestClient) -> None:
    response = client.post("/api/workflow-runs/999/reject", json=approval_body())

    assert response.status_code == 404


def test_cannot_approve_same_workflow_twice(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = create_executed_high_risk_workflow(client)

    first_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/approve",
        json=approval_body("First approval."),
    )
    second_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/approve",
        json=approval_body("Duplicate approval."),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert len(get_approval_decisions(db_session, int(workflow_run["id"]))) == 1


def test_cannot_reject_same_workflow_twice(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = create_executed_high_risk_workflow(client)

    first_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/reject",
        json=approval_body("First rejection."),
    )
    second_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/reject",
        json=approval_body("Duplicate rejection."),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409
    assert len(get_approval_decisions(db_session, int(workflow_run["id"]))) == 1


def test_cannot_reject_after_approval(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = create_executed_high_risk_workflow(client)

    approve_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/approve",
        json=approval_body("Approved."),
    )
    reject_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/reject",
        json=approval_body("Reject after approval."),
    )

    assert approve_response.status_code == 200
    assert reject_response.status_code == 409
    assert len(get_approval_decisions(db_session, int(workflow_run["id"]))) == 1


def test_cannot_approve_after_rejection(
    client: TestClient,
    db_session: Session,
) -> None:
    workflow_run = create_executed_high_risk_workflow(client)

    reject_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/reject",
        json=approval_body("Rejected."),
    )
    approve_response = client.post(
        f"/api/workflow-runs/{workflow_run['id']}/approve",
        json=approval_body("Approve after rejection."),
    )

    assert reject_response.status_code == 200
    assert approve_response.status_code == 409
    assert len(get_approval_decisions(db_session, int(workflow_run["id"]))) == 1
