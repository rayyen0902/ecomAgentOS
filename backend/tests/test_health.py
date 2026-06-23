"""Tests for the /api/v1/health endpoint."""

import re
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

ISO8601_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def test_health_check() -> None:
    """GET /api/v1/health returns a valid health check response."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "0.1.0"
    assert ISO8601_UTC_RE.match(data["timestamp"])

    # Verify the timestamp is a plausible recent UTC time.
    parsed = datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )
    now = datetime.now(timezone.utc)
    assert abs((now - parsed).total_seconds()) < 5
