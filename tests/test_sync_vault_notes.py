import json
from pathlib import Path
from scripts.sync_vault_notes import (
    sanitize_filename,
    format_markdown_note,
    sync_notes_to_directory
)


def test_sanitize_filename():
    assert sanitize_filename("Note: An Introduction / Overview?") == "Note_ An Introduction _ Overview_"
    assert sanitize_filename("") == "untitled"
    assert sanitize_filename("   ") == "untitled"


def test_format_markdown_note():
    note = {
        "id": "note-123456",
        "title": "Tư duy phản biện",
        "source_book": "Thinking Fast and Slow",
        "category": "Philosophy",
        "tags": ["book", "psychology"],
        "links": ["Daniel Kahneman"],
        "created_at": "2026-11-01T12:00:00",
        "updated_at": "2026-11-01T12:00:00",
        "content_raw": "Hệ thống 1 và Hệ thống 2 điều khiển tư duy."
    }
    md = format_markdown_note(note)
    assert "---" in md
    assert "title: Tư duy phản biện" in md
    assert "source_book: Thinking Fast and Slow" in md
    assert "# Tư duy phản biện" in md
    assert "Hệ thống 1 và Hệ thống 2 điều khiển tư duy." in md


def test_sync_notes_to_directory(tmp_path: Path):
    notes = [
        {
            "id": "note-abc1",
            "title": "Ghi chú 1",
            "source_book": "Atomic Habits",
            "updated_at": "2026-11-01T10:00:00",
            "content_raw": "Quy tắc 1% mỗi ngày."
        },
        {
            "id": "note-abc2",
            "title": "Ghi chú 2",
            "source_book": "",
            "updated_at": "2026-11-01T11:00:00",
            "content_raw": "Ghi chú tự do."
        }
    ]

    # First sync
    res1 = sync_notes_to_directory(notes, tmp_path, group_by_book=True)
    assert res1["synced"] == 2
    assert res1["skipped"] == 0

    book_dir = tmp_path / "Atomic Habits"
    assert book_dir.exists()
    assert len(list(book_dir.glob("*.md"))) == 1
    assert len(list(tmp_path.glob("*.md"))) == 1

    manifest_file = tmp_path / ".sync_manifest.json"
    assert manifest_file.exists()
    with open(manifest_file, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    assert manifest["note-abc1"] == "2026-11-01T10:00:00"

    # Second sync without changes -> should skip all
    res2 = sync_notes_to_directory(notes, tmp_path, group_by_book=True)
    assert res2["synced"] == 0
    assert res2["skipped"] == 2

    # Update note 1
    notes[0]["updated_at"] = "2026-11-01T12:00:00"
    res3 = sync_notes_to_directory(notes, tmp_path, group_by_book=True)
    assert res3["synced"] == 1
    assert res3["skipped"] == 1
