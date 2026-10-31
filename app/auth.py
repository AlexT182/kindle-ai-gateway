import base64
import hashlib
import hmac
import secrets
import time
from collections import defaultdict, deque
from typing import Optional

from fastapi import Header, HTTPException, Request, status

from app.config import settings


def _constant_time_equal(candidate: str, expected: str) -> bool:
    return bool(candidate and expected) and secrets.compare_digest(candidate, expected)


def require_api_token(
    request: Request,
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Header(None, alias="api-key"),
) -> bool:
    candidates = [x_api_key or "", api_key or ""]
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer" and value:
            candidates.append(value.strip())
    if any(_constant_time_equal(value, settings.AUTH_TOKEN) for value in candidates):
        client_ip = request.client.host if request.client else "unknown"
        token_fingerprint = hashlib.sha256(settings.AUTH_TOKEN.encode()).hexdigest()[:16]
        if not _sliding_window_allowed(_api_requests, f"{client_ip}:{token_fingerprint}", 120, 60):
            raise HTTPException(429, "API rate limit exceeded")
        return True
    raise HTTPException(401, "Missing or invalid API token", headers={"WWW-Authenticate": "Bearer"})


def verify_admin_password(candidate: str) -> bool:
    return _constant_time_equal(candidate, settings.ADMIN_PASSWORD)


def _sign(value: str) -> str:
    return hmac.new(settings.SESSION_SECRET.encode(), value.encode(), hashlib.sha256).hexdigest()


def create_admin_session() -> str:
    payload = f"{int(time.time())}.{secrets.token_urlsafe(18)}"
    return base64.urlsafe_b64encode(f"{payload}.{_sign(payload)}".encode()).decode()


def is_admin_session_valid(token: Optional[str]) -> bool:
    if not token:
        return False
    try:
        raw = base64.urlsafe_b64decode(token.encode()).decode()
        issued, nonce, signature = raw.split(".", 2)
        payload = f"{issued}.{nonce}"
        age = int(time.time()) - int(issued)
        return 0 <= age <= settings.SESSION_MAX_AGE and secrets.compare_digest(signature, _sign(payload))
    except (ValueError, TypeError, UnicodeDecodeError):
        return False


def csrf_token(session_token: str) -> str:
    return hmac.new(settings.SESSION_SECRET.encode(), f"csrf:{session_token}".encode(), hashlib.sha256).hexdigest()


def validate_csrf(request: Request, supplied: Optional[str]) -> None:
    session = request.cookies.get("admin_session", "")
    if not supplied or not session or not secrets.compare_digest(supplied, csrf_token(session)):
        raise HTTPException(status_code=403, detail="Invalid CSRF token")


_login_attempts = defaultdict(deque)
_api_requests = defaultdict(deque)


def _sliding_window_allowed(store, key: str, limit: int, window_seconds: int) -> bool:
    now = time.monotonic()
    events = store[key]
    while events and now - events[0] > window_seconds:
        events.popleft()
    if len(events) >= limit:
        return False
    events.append(now)
    return True


def login_allowed(client_ip: str, limit: int = 5, window_seconds: int = 300) -> bool:
    now = time.monotonic()
    attempts = _login_attempts[client_ip]
    while attempts and now - attempts[0] > window_seconds:
        attempts.popleft()
    if len(attempts) >= limit:
        return False
    return True


def record_failed_login(client_ip: str) -> None:
    _login_attempts[client_ip].append(time.monotonic())


def clear_login_failures(client_ip: str) -> None:
    _login_attempts.pop(client_ip, None)
