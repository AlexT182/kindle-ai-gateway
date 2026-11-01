"""Read-only production smoke checks for Kindle AI Gateway.

Usage (PowerShell):
    $env:BASE_URL = "https://kindle.alphatech.ai.vn"
    $env:AUTH_TOKEN = "<machine token>"
    python scripts/smoke_production.py
"""

import os
import sys

import httpx


def run_checks(client, token: str) -> list[str]:
    results = []

    health = client.get("/health")
    assert health.status_code == 200, f"health returned {health.status_code}"
    assert health.json().get("status") == "healthy", "health payload is not healthy"
    results.append("health: healthy")

    login = client.get("/admin/login")
    assert login.status_code == 200, f"admin login returned {login.status_code}"
    results.append("admin login: reachable")

    unauth_models = client.get("/v1/models")
    assert unauth_models.status_code == 401, f"models without token returned {unauth_models.status_code}"
    results.append("API auth: rejects missing token")

    headers = {"Authorization": f"Bearer {token}"}
    models = client.get("/v1/models", headers=headers)
    assert models.status_code == 200, f"models with token returned {models.status_code}"
    model_ids = {item.get("id") for item in models.json().get("data", [])}
    assert "alex-agent" in model_ids, "alex-agent is missing from model list"
    results.append("API auth: valid token accepted")

    graph = client.get("/v1/vault/graph/image")
    assert graph.status_code == 401, f"graph image without token returned {graph.status_code}"
    results.append("Vault graph: protected")

    cors = client.get("/health", headers={"Origin": "https://evil.example"})
    assert cors.headers.get("access-control-allow-origin") is None, "arbitrary CORS origin was accepted"
    results.append("CORS: arbitrary origin rejected")
    return results


def main() -> int:
    base_url = os.getenv("BASE_URL", "https://kindle.alphatech.ai.vn").rstrip("/")
    token = os.getenv("AUTH_TOKEN", "")
    if len(token) < 32:
        print("ERROR: set AUTH_TOKEN to the production machine token", file=sys.stderr)
        return 2
    try:
        with httpx.Client(base_url=base_url, timeout=15, follow_redirects=False) as client:
            results = run_checks(client, token)
    except (AssertionError, httpx.HTTPError, ValueError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1
    for result in results:
        print(f"OK: {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
