from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from scripts.smoke_production import run_checks


def test_read_only_smoke_checks(monkeypatch):
    token = "smoke-token-" + "x" * 40
    monkeypatch.setattr(settings, "AUTH_TOKEN", token)
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", "admin-password-long-enough")
    monkeypatch.setattr(settings, "SESSION_SECRET", "session-secret-" + "s" * 40)
    monkeypatch.setattr(settings, "ENABLE_SCHEDULER", False)
    with TestClient(app, base_url="https://testserver") as client:
        results = run_checks(client, token)
    assert len(results) == 6
