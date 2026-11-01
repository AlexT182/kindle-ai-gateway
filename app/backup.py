import json
import shutil
import sqlite3
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Tuple

from app.config import settings
from app.db import get_connection

DATA_DIR = settings.DATA_DIR
DB_SIDECARS = {"vault.db", "vault.db-wal", "vault.db-shm"}
STALE_BACKUP_SECONDS = 24 * 60 * 60


def cleanup_stale_backups(temp_parent: Path) -> None:
    cutoff = time.time() - STALE_BACKUP_SECONDS
    for candidate in temp_parent.glob("kindle-vault-backup-*"):
        try:
            if candidate.is_dir() and candidate.stat().st_mtime < cutoff:
                shutil.rmtree(candidate, ignore_errors=True)
        except OSError:
            continue


def create_vault_backup() -> Tuple[Path, Path]:
    data_root = Path(DATA_DIR).resolve()
    temp_parent = data_root / ".tmp"
    temp_parent.mkdir(parents=True, exist_ok=True)
    cleanup_stale_backups(temp_parent)
    temp_root = Path(tempfile.mkdtemp(prefix="kindle-vault-backup-", dir=temp_parent))
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    snapshot_path = temp_root / "vault.db"
    archive_path = temp_root / f"kindle-vault-{timestamp}.zip"

    try:
        source = get_connection()
        try:
            destination = sqlite3.connect(snapshot_path)
            try:
                source.backup(destination)
            finally:
                destination.close()
        finally:
            source.close()

        manifest = {
            "format": "kindle-ai-vault-backup",
            "version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.write(snapshot_path, "vault.db")
            archive.writestr("manifest.json", json.dumps(manifest, indent=2))
            if data_root.exists():
                for path in data_root.rglob("*"):
                    if not path.is_file() or path.is_symlink() or path.name in DB_SIDECARS:
                        continue
                    resolved = path.resolve()
                    if not resolved.is_relative_to(data_root) or resolved.is_relative_to(temp_parent):
                        continue
                    archive.write(resolved, resolved.relative_to(data_root).as_posix())
        return archive_path, temp_root
    except Exception:
        shutil.rmtree(temp_root, ignore_errors=True)
        raise


def cleanup_backup(temp_root: Path) -> None:
    shutil.rmtree(temp_root, ignore_errors=True)
