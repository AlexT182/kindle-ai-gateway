import pytest
from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.auth import clear_login_failures, login_allowed, record_failed_login


API_TOKEN = "api-token-" + "a" * 40
ADMIN_PASSWORD = "admin-password-long-enough"
SESSION_SECRET = "session-secret-" + "s" * 40


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setattr(settings, "AUTH_TOKEN", API_TOKEN)
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", ADMIN_PASSWORD)
    monkeypatch.setattr(settings, "SESSION_SECRET", SESSION_SECRET)
    monkeypatch.setattr(settings, "ENABLE_SCHEDULER", False)
    with TestClient(app, base_url="https://testserver") as test_client:
        yield test_client


def test_protected_api_rejects_missing_invalid_and_query_tokens(client):
    assert client.get("/v1/models").status_code == 401
    assert client.get("/v1/models", headers={"Authorization": "Bearer wrong"}).status_code == 401
    assert client.get(f"/v1/models?token={API_TOKEN}").status_code == 401


def test_protected_api_accepts_bearer_and_api_key_headers(client):
    assert client.get("/v1/models", headers={"Authorization": f"Bearer {API_TOKEN}"}).status_code == 200
    assert client.get("/v1/models", headers={"X-API-Key": API_TOKEN}).status_code == 200


def test_graph_image_is_protected(client):
    assert client.get("/v1/vault/graph/image").status_code == 401


def test_arbitrary_origin_is_not_allowed(client):
    response = client.get("/health", headers={"Origin": "https://evil.example"})
    assert response.headers.get("access-control-allow-origin") is None


def test_admin_login_uses_signed_secure_cookie_not_password(client):
    response = client.post("/admin/login", data={"password": ADMIN_PASSWORD}, follow_redirects=False)
    assert response.status_code == 303
    cookie = response.headers["set-cookie"]
    assert ADMIN_PASSWORD not in cookie
    assert API_TOKEN not in cookie
    assert "HttpOnly" in cookie
    assert "Secure" in cookie
    assert "SameSite=strict" in cookie


def test_admin_rejects_query_password(client):
    response = client.get(f"/admin?token={ADMIN_PASSWORD}", follow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"


def test_admin_write_requires_csrf(client):
    login = client.post("/admin/login", data={"password": ADMIN_PASSWORD}, follow_redirects=False)
    assert login.status_code == 303
    response = client.post("/admin/notes/create", data={"title": "x", "content": "y"})
    assert response.status_code == 403


def test_request_bounds_are_enforced_before_provider_call(client, monkeypatch):
    monkeypatch.setattr(settings, "DEEPSEEK_API_KEY", "configured")
    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": "hello"}], "max_tokens": settings.MAX_OUTPUT_TOKENS + 1},
    )
    assert response.status_code == 422


def test_security_validation_rejects_defaults(monkeypatch):
    monkeypatch.setattr(settings, "AUTH_TOKEN", "kindle-secret-token")
    monkeypatch.setattr(settings, "ADMIN_PASSWORD", "password")
    monkeypatch.setattr(settings, "SESSION_SECRET", "short")
    with pytest.raises(RuntimeError, match="Unsafe configuration"):
        settings.validate_security()


def test_login_rate_limit_counts_only_failures():
    ip = "test-rate-limit"
    clear_login_failures(ip)
    for _ in range(5):
        assert login_allowed(ip)
        record_failed_login(ip)
    assert not login_allowed(ip)
    clear_login_failures(ip)
    assert login_allowed(ip)
