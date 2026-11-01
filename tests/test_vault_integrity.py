from pathlib import Path

import pytest

from app import db, vault
from app.main import public_note


@pytest.fixture()
def isolated_vault(tmp_path, monkeypatch):
    notes_dir = tmp_path / "vault" / "notes"
    notes_dir.mkdir(parents=True)
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "vault.db"))
    monkeypatch.setattr(vault, "NOTES_DIR", str(notes_dir))
    db.init_db()
    return notes_dir


def test_same_title_same_second_creates_distinct_notes(isolated_vault):
    first = vault.save_note_to_vault("First", title="Same title")
    second = vault.save_note_to_vault("Second", title="Same title")

    assert first["id"] != second["id"]
    assert first["file_path"] != second["file_path"]
    assert Path(first["file_path"]).exists()
    assert Path(second["file_path"]).exists()
    assert len(db.get_all_notes_db()) == 2


def test_delete_removes_index_and_markdown_file(isolated_vault):
    note = vault.save_note_to_vault("Delete me", title="Disposable")
    file_path = Path(note["file_path"])

    assert vault.delete_note_from_vault(note["id"]) is True
    assert db.get_note_db(note["id"]) is None
    assert not file_path.exists()
    assert vault.delete_note_from_vault(note["id"]) is False


def test_failed_index_write_cleans_up_markdown(isolated_vault, monkeypatch):
    def fail_index(**_):
        raise RuntimeError("database unavailable")

    monkeypatch.setattr(vault, "upsert_note_index", fail_index)
    with pytest.raises(RuntimeError, match="database unavailable"):
        vault.save_note_to_vault("Must roll back", title="Rollback")
    assert list(isolated_vault.iterdir()) == []


def test_delete_refuses_file_outside_vault(isolated_vault, tmp_path):
    outside = tmp_path / "outside.md"
    outside.write_text("keep", encoding="utf-8")
    db.upsert_note_index("unsafe", "Unsafe", str(outside), "", "General", "x", [], [], "now", "now")

    with pytest.raises(ValueError, match="outside"):
        vault.delete_note_from_vault("unsafe")
    assert outside.exists()
    assert db.get_note_db("unsafe") is not None


def test_public_note_never_exposes_server_path():
    note = {"id": "n1", "title": "Safe", "file_path": "/data/private/n1.md"}
    assert public_note(note) == {"id": "n1", "title": "Safe"}


def test_usage_summary_contains_only_operational_metadata(isolated_vault):
    assert db.record_usage_event("req-1", "alex-agent", False, "success", 125.5, 10, 5, 15, 2)
    assert db.record_usage_event("req-2", "alex-agent", True, "error", 250.0)
    summary = db.get_usage_summary(days=7)
    assert summary["requests"] == 2
    assert summary["total_tokens"] == 15
    assert summary["tool_calls"] == 2
    assert summary["errors"] == 1

    connection = db.get_connection()
    try:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(usage_events)")}
    finally:
        connection.close()
    assert not ({"prompt", "response", "ip", "api_token"} & columns)
