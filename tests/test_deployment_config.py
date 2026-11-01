from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parent.parent


def test_compose_has_durable_data_and_container_hardening():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text(encoding="utf-8"))
    service = compose["services"]["kindle-ai-gateway"]
    assert "kindle_ai_data:/data" in service["volumes"]
    assert service["read_only"] is True
    assert "ALL" in service["cap_drop"]
    assert "no-new-privileges:true" in service["security_opt"]
    assert "healthcheck" in service


def test_dockerfile_runs_as_non_root_and_uses_lockfile():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "USER app" in dockerfile
    assert "requirements.lock" in dockerfile
    assert "COPY . ." not in dockerfile
    assert "--forwarded-allow-ips=*" not in dockerfile
    assert "--no-access-log" in dockerfile


def test_runtime_data_and_secrets_are_ignored():
    ignored = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in ignored
    assert "data/" in ignored
    assert ".gstack/" in ignored
