from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_optimize_works_without_api_key_when_auth_disabled() -> None:
    response = client.post(
        "/optimize",
        json={"prompt": "Please summarize this content clearly.", "mode": "eco"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "optimized_prompt" in data
    assert data["tokens_before"] > 0
    assert data["tokens_after"] > 0


def test_usage_works_without_api_key_when_auth_disabled() -> None:
    response = client.get("/usage")
    assert response.status_code == 200
    assert "total_requests" in response.json()
