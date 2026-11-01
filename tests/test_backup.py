import json
import sqlite3
import zipfile
from pathlib import Path

from app import backup, db, vault


def test_backup_contains_consistent_database_and_vault_files(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    notes_dir = data_dir / "vault" / "notes"
    notes_dir.mkdir(parents=True)
    monkeypatch.setattr(db, "DB_PATH", str(data_dir / "vault.db"))
    monkeypatch.setattr(vault, "NOTES_DIR", str(notes_dir))
    monkeypatch.setattr(backup, "DATA_DIR", data_dir)
    db.init_db()
    note = vault.save_note_to_vault("Backup content", title="Backup note")
    config_dir = data_dir / "config"
    config_dir.mkdir()
    (config_dir / "persona.json").write_text('{"name":"Alex"}', encoding="utf-8")

    archive_path, temp_root = backup.create_vault_backup()
    try:
        with zipfile.ZipFile(archive_path) as archive:
            names = set(archive.namelist())
            assert "vault.db" in names
            assert "manifest.json" in names
            assert "config/persona.json" in names
            relative_note = Path(note["file_path"]).relative_to(data_dir).as_posix()
            assert relative_note in names
            assert json.loads(archive.read("manifest.json"))["version"] == 1
            extracted_db = tmp_path / "restored.db"
            extracted_db.write_bytes(archive.read("vault.db"))
        connection = sqlite3.connect(extracted_db)
        try:
            assert connection.execute("SELECT COUNT(*) FROM notes").fetchone()[0] == 1
        finally:
            connection.close()
    finally:
        backup.cleanup_backup(temp_root)
    assert not temp_root.exists()
