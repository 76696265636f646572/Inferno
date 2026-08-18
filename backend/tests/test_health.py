from __future__ import annotations

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.core.errors import APIError
from app.main import create_app


def test_health_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Inferno"
    assert "time" in body
    assert response.headers.get("X-Request-ID")


def test_ready_ok(client: TestClient) -> None:
    response = client.get("/api/v1/system/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    names = {check["name"] for check in body["checks"]}
    assert names == {"database", "storage"}
    assert all(check["healthy"] for check in body["checks"])


def test_system_info(client: TestClient) -> None:
    response = client.get("/api/v1/system/info")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "Inferno"
    assert body["auth_enabled"] is False
    assert "model_storage_path" in body


def test_openapi_includes_required_tags(client: TestClient) -> None:
    spec = client.get("/openapi.json").json()
    names = {tag["name"] for tag in spec["tags"]}
    assert names >= {
        "Models",
        "Downloads",
        "Runtimes",
        "Inference",
        "Analytics",
        "Authentication",
        "API Keys",
        "System",
    }


def test_websocket_hello(client: TestClient) -> None:
    with client.websocket_connect("/ws") as ws:
        event = ws.receive_json()
    assert event["type"] == "system.status"
    assert event["data"]["status"] == "healthy"
    assert "timestamp" in event


def test_error_envelope(tmp_settings: Settings) -> None:
    application = create_app(tmp_settings)

    @application.get("/boom")
    async def boom() -> None:
        raise APIError("MODEL_NOT_FOUND", "The requested model does not exist.", status_code=404)

    with TestClient(application) as test_client:
        response = test_client.get("/boom")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "MODEL_NOT_FOUND",
            "message": "The requested model does not exist.",
        }
    }


def test_unhandled_error_does_not_leak(tmp_settings: Settings) -> None:
    application = create_app(tmp_settings)

    @application.get("/crash")
    async def crash() -> None:
        raise RuntimeError("secret internals")

    with TestClient(application, raise_server_exceptions=False) as test_client:
        response = test_client.get("/crash")
    assert response.status_code == 500
    body = response.json()
    assert body["error"]["code"] == "INTERNAL_ERROR"
    assert "secret internals" not in str(body)
