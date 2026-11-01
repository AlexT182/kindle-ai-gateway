"""Sync Vault notes from Kindle AI Gateway to a local Markdown directory (e.g. for Obsidian).

Features:
- Incremental sync: Only writes/updates notes when modified.
- Obsidian-ready Markdown: YAML frontmatter, tags, [[wikilinks]], source book.
- Configurable destination directory and book-based subfolder grouping.

Usage (PowerShell):
    python scripts/sync_vault_notes.py --output-dir D:/QQ/kindle/vault_notes
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import dotenv
import httpx
import yaml


def sanitize_filename(name: str) -> str:
    """Sanitize string to be safe for filenames across Windows and Unix."""
    cleaned = re.sub(r'[\\/*?:"<>|]', "_", name).strip()
    return cleaned[:60] if cleaned else "untitled"


def format_markdown_note(note: Dict[str, Any]) -> str:
    """Format note dictionary into Obsidian-compatible Markdown with YAML frontmatter."""
    title = note.get("title") or "Untitled Note"
    source_book = note.get("source_book") or ""
    category = note.get("category") or "General"
    tags = note.get("tags") or []
    links = note.get("links") or []
    created_at = note.get("created_at") or datetime.now().isoformat()
    updated_at = note.get("updated_at") or created_at
    content = note.get("content_raw") or ""

    frontmatter = {
        "id": note.get("id") or note.get("note_id"),
        "title": title,
        "source_book": source_book,
        "category": category,
        "tags": tags,
        "links": links,
        "created_at": created_at,
        "updated_at": updated_at,
    }

    yaml_block = yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)
    return f"---\n{yaml_block}---\n\n# {title}\n\n{content.strip()}\n"


def fetch_vault_notes(
    base_url: str,
    token: str,
    limit: int = 100,
    query: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Fetch all notes from the gateway vault API."""
    url = f"{base_url.rstrip('/')}/v1/vault/notes"
    headers = {"Authorization": f"Bearer {token}"}
    params: Dict[str, Any] = {"limit": limit}
    if query:
        params["q"] = query

    with httpx.Client(timeout=15) as client:
        response = client.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        if isinstance(data, list):
            return data
        return []


def sync_notes_to_directory(
    notes: List[Dict[str, Any]],
    output_dir: Path,
    group_by_book: bool = True
) -> Dict[str, int]:
    """Sync list of notes to the specified local directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    synced = 0
    skipped = 0

    manifest_path = output_dir / ".sync_manifest.json"
    manifest: Dict[str, str] = {}
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception:
            manifest = {}

    for note in notes:
        note_id = note.get("id") or note.get("note_id") or ""
        updated_at = note.get("updated_at") or ""
        if not note_id:
            continue

        # Skip if already synced and updated_at has not changed
        if manifest.get(note_id) == updated_at:
            skipped += 1
            continue

        title = note.get("title") or "note"
        source_book = note.get("source_book") or ""
        
        target_dir = output_dir
        if group_by_book and source_book.strip():
            safe_book = sanitize_filename(source_book)
            target_dir = output_dir / safe_book
            target_dir.mkdir(parents=True, exist_ok=True)

        safe_title = sanitize_filename(title)
        short_id = note_id[-8:] if len(note_id) >= 8 else note_id
        file_path = target_dir / f"{safe_title}_{short_id}.md"

        content = format_markdown_note(note)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        manifest[note_id] = updated_at
        synced += 1

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return {"synced": synced, "skipped": skipped, "total": len(notes)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Kindle AI Gateway Vault notes to local Markdown folder.")
    parser.add_argument("--base-url", default=os.getenv("BASE_URL", "https://kindle.alphatech.ai.vn"), help="Gateway URL")
    parser.add_argument("--token", default=os.getenv("AUTH_TOKEN", ""), help="Auth token")
    parser.add_argument("--output-dir", default="D:/QQ/kindle/vault_notes", help="Destination folder")
    parser.add_argument("--no-group", action="store_true", help="Do not group notes into book subfolders")
    args = parser.parse_args()

    dotenv.load_dotenv(Path(__file__).parent.parent / ".env")
    token = args.token or os.getenv("AUTH_TOKEN", "")

    if not token or len(token) < 10:
        print("ERROR: Missing or invalid AUTH_TOKEN.", file=sys.stderr)
        return 1

    try:
        notes = fetch_vault_notes(args.base_url, token)
        result = sync_notes_to_directory(notes, Path(args.output_dir), group_by_book=not args.no_group)
        print(f"Sync complete: {result['synced']} written/updated, {result['skipped']} unchanged, {result['total']} total notes.")
        return 0
    except Exception as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
