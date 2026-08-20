import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "vault.db")

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Notes Metadata Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        file_path TEXT NOT NULL UNIQUE,
        source_book TEXT,
        category TEXT DEFAULT 'General',
        content_raw TEXT,
        created_at TEXT,
        updated_at TEXT
    )
    ''')
    
    # 2. Note Tags Table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS note_tags (
        note_id TEXT,
        tag TEXT,
        PRIMARY KEY (note_id, tag),
        FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE CASCADE
    )
    ''')
    
    # 3. Note Links Table (Knowledge Graph Edges)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS note_links (
        source_node TEXT,
        target_node TEXT,
        link_type TEXT DEFAULT 'related',
        PRIMARY KEY (source_node, target_node)
    )
    ''')
    
    # 4. Full-Text Search FTS5 Table
    cursor.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS notes_fts USING fts5(
        id UNINDEXED,
        title,
        content_raw,
        tags,
        tokenize = 'unicode61'
    )
    ''')
    
    conn.commit()
    conn.close()

def upsert_note_index(note_id: str, title: str, file_path: str, source_book: str, category: str, content_raw: str, tags: List[str], links: List[str], created_at: str, updated_at: str):
    conn = get_connection()
    cursor = conn.cursor()
    
    # Upsert notes table
    cursor.execute('''
    INSERT OR REPLACE INTO notes (id, title, file_path, source_book, category, content_raw, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (note_id, title, file_path, source_book, category, content_raw, created_at, updated_at))
    
    # Update tags
    cursor.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
    for tag in tags:
        cursor.execute('INSERT OR IGNORE INTO note_tags (note_id, tag) VALUES (?, ?)', (note_id, tag.strip().lower()))
        
    # Update links (Graph edges)
    cursor.execute('DELETE FROM note_links WHERE source_node = ?', (title,))
    for target in links:
        if target.strip():
            cursor.execute('INSERT OR IGNORE INTO note_links (source_node, target_node, link_type) VALUES (?, ?, ?)', (title, target.strip(), 'references'))
    
    # If source book is present, link book -> note
    if source_book and source_book.strip():
        cursor.execute('INSERT OR IGNORE INTO note_links (source_node, target_node, link_type) VALUES (?, ?, ?)', (source_book.strip(), title, 'contains'))

    # Update FTS5
    cursor.execute('DELETE FROM notes_fts WHERE id = ?', (note_id,))
    tags_str = " ".join(tags)
    cursor.execute('INSERT INTO notes_fts (id, title, content_raw, tags) VALUES (?, ?, ?, ?)', (note_id, title, content_raw, tags_str))
    
    conn.commit()
    conn.close()

def delete_note_index(note_id: str, title: str = ""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
    cursor.execute('DELETE FROM note_tags WHERE note_id = ?', (note_id,))
    cursor.execute('DELETE FROM notes_fts WHERE id = ?', (note_id,))
    if title:
        cursor.execute('DELETE FROM note_links WHERE source_node = ? OR target_node = ?', (title, title))
    conn.commit()
    conn.close()

def search_notes_fts(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    
    # Sanitize query for FTS5
    clean_q = "".join(c for c in query if c.isalnum() or c.isspace())
    if not clean_q.strip():
        return get_all_notes_db(limit=limit)
        
    terms = clean_q.strip().split()
    fts_match = " OR ".join(f'"{t}"*' for t in terms)
    
    try:
        cursor.execute('''
        SELECT n.id, n.title, n.file_path, n.source_book, n.category, n.content_raw, n.created_at, n.updated_at
        FROM notes_fts f
        JOIN notes n ON f.id = n.id
        WHERE notes_fts MATCH ?
        ORDER BY rank
        LIMIT ?
        ''', (fts_match, limit))
        rows = cursor.fetchall()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[DB Search Error]: {e}")
        return get_all_notes_db(limit=limit)
    finally:
        conn.close()

def get_all_notes_db(limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
    SELECT id, title, file_path, source_book, category, content_raw, created_at, updated_at
    FROM notes
    ORDER BY created_at DESC
    LIMIT ? OFFSET ?
    ''', (limit, offset))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_graph_edges() -> List[Dict[str, str]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT source_node, target_node, link_type FROM note_links')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_tags() -> List[Dict[str, Any]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT tag, COUNT(*) as count FROM note_tags GROUP BY tag ORDER BY count DESC')
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

# Initialize database on module load
init_db()
