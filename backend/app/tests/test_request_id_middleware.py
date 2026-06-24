from uuid import UUID

from fastapi.testclient import TestClient

from app.core.request_context import TRACE_ID_HEADER
from app.main import app


def test_response_includes_generated_request_id_header() -> None:
    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200
    generated_trace_id = response.headers[TRACE_ID_HEADER]
    assert UUID(generated_trace_id)


def test_response_reuses_provided_request_id_header() -> None:
    client = TestClient(app)
    provided_trace_id = "phase-13-request-id"

    response = client.get("/health", headers={TRACE_ID_HEADER: provided_trace_id})

    assert response.status_code == 200
    assert response.headers[TRACE_ID_HEADER] == provided_trace_id
