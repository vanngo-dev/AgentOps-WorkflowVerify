from fastapi.testclient import TestClient


def test_app_imports() -> None:
    from app.main import app

    assert app is not None


def test_health_returns_200() -> None:
    from app.main import app

    client = TestClient(app)

    response = client.get("/health")

    assert response.status_code == 200


def test_health_returns_status_ok() -> None:
    from app.main import app

    client = TestClient(app)

    response = client.get("/health")

    assert response.json() == {"status": "ok"}


def test_ready_returns_200() -> None:
    from app.main import app

    client = TestClient(app)

    response = client.get("/ready")

    assert response.status_code == 200


def test_ready_returns_status_ready() -> None:
    from app.main import app

    client = TestClient(app)

    response = client.get("/ready")

    assert response.json() == {"status": "ready"}


def test_cors_allows_vite_frontend_origin() -> None:
    from app.main import app

    client = TestClient(app)

    response = client.options(
        "/health",
        headers={
            "Access-Control-Request-Method": "GET",
            "Origin": "http://localhost:5173",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == (
        "http://localhost:5173"
    )
