from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.services.rate_limiter import clear_rate_limit_state


client = TestClient(app)


def test_ip_rate_limit_blocks_excess_requests() -> None:
    prev_enabled = settings.rate_limit_enabled
    prev_limit = settings.rate_limit_requests_per_minute
    settings.rate_limit_enabled = True
    settings.rate_limit_requests_per_minute = 2
    clear_rate_limit_state()

    try:
        one = client.post("/optimize", json={"prompt": "p1", "mode": "eco"})
        two = client.post("/optimize", json={"prompt": "p2", "mode": "eco"})
        three = client.post("/optimize", json={"prompt": "p3", "mode": "eco"})

        assert one.status_code == 200
        assert two.status_code == 200
        assert three.status_code == 429
    finally:
        settings.rate_limit_enabled = prev_enabled
        settings.rate_limit_requests_per_minute = prev_limit
        clear_rate_limit_state()
