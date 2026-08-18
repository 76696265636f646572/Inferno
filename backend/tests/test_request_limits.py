from __future__ import annotations

from fastapi.testclient import TestClient


def test_rejects_oversized_content_length(client: TestClient) -> None:
    response = client.post(
        "/api/v1/system/info",
        content=b"unused",
        headers={"Content-Length": str(20 * 1024 * 1024)},
    )
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "REQUEST_TOO_LARGE"
