from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models import WorkflowRun


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
            "name": "sample vendor invoice review",
            "input_payload": {
                "vendor": "Acme Supplies",
                "amount": 1250.00,
                "invoice_id": "INV-1001",
            },
        },
    )

    assert response.status_code == 201
    return response.json()


def test_post_workflow_runs_creates_workflow_run(client: TestClient) -> None:
    data = create_workflow_run(client)

    assert data["id"] is not None
    assert data["name"] == "sample vendor invoice review"
    assert data["input_payload"] == {
        "vendor": "Acme Supplies",
        "amount": 1250.00,
        "invoice_id": "INV-1001",
    }
    assert data["created_at"] is not None
    assert data["updated_at"] is not None


def test_created_workflow_run_starts_created(client: TestClient) -> None:
    data = create_workflow_run(client)

    assert data["status"] == "created"


def test_created_workflow_run_starts_unknown_risk(client: TestClient) -> None:
    data = create_workflow_run(client)

    assert data["risk_level"] == "unknown"


def test_created_workflow_run_has_empty_execution_outputs(
    client: TestClient,
) -> None:
    data = create_workflow_run(client)

    assert data["output_payload"] is None
    assert data["completed_at"] is None


def test_get_workflow_runs_lists_workflow_runs(
    client: TestClient,
    db_session: Session,
) -> None:
    db_session.add(
        WorkflowRun(name="Existing workflow", input_payload={"source": "fixture"}),
    )
    db_session.commit()

    response = client.get("/api/workflow-runs")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "Existing workflow"


def test_get_workflow_run_by_id_returns_one_workflow_run(client: TestClient) -> None:
    created = create_workflow_run(client)

    response = client.get(f"/api/workflow-runs/{created['id']}")

    assert response.status_code == 200
    assert response.json()["id"] == created["id"]
    assert response.json()["name"] == "sample vendor invoice review"


def test_get_workflow_run_by_invalid_id_returns_404(client: TestClient) -> None:
    response = client.get("/api/workflow-runs/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Workflow run not found."}


def test_invalid_post_body_returns_422(client: TestClient) -> None:
    response = client.post(
        "/api/workflow-runs",
        json={"input_payload": {"invoice_id": "INV-1001"}},
    )

    assert response.status_code == 422
