import os
import re
import yaml
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

from app.db import (
    upsert_note_index,
    delete_note_index,
    search_notes_fts,
    get_all_notes_db,
    get_graph_edges,
    get_all_tags
)

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
VAULT_DIR = os.path.join(DATA_DIR, "vault")
NOTES_DIR = os.path.join(VAULT_DIR, "notes")
BOOKS_DIR = os.path.join(VAULT_DIR, "books")
DIGESTS_DIR = os.path.join(VAULT_DIR, "digests")

os.makedirs(NOTES_DIR, exist_ok=True)
os.makedirs(BOOKS_DIR, exist_ok=True)
os.makedirs(DIGESTS_DIR, exist_ok=True)

def extract_wikilinks(content: str) -> List[str]:
    # Extracts [[Node Name]] or [[Node Name|Alias]]
    matches = re.findall(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]', content)
    return [m.strip() for m in matches if m.strip()]

def extract_hashtags(content: str) -> List[str]:
    # Extracts #tag
    matches = re.findall(r'(?:^|\s)#([a-zA-Z0-9_\-]+)', content)
    return [m.strip().lower() for m in matches if m.strip()]

def parse_markdown_file(file_path: str) -> Optional[Dict[str, Any]]:
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw = f.read()
        
        frontmatter = {}
        body = raw
        
        # Check for YAML Frontmatter
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                try:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    body = parts[2].strip()
                except Exception:
                    body = raw
                    
        return {
            "id": frontmatter.get("id", os.path.splitext(os.path.basename(file_path))[0]),
            "title": frontmatter.get("title", os.path.splitext(os.path.basename(file_path))[0]),
            "source_book": frontmatter.get("source_book", ""),
            "category": frontmatter.get("category", "General"),
            "tags": frontmatter.get("tags", []),
            "related_nodes": frontmatter.get("related_nodes", []),
            "created_at": frontmatter.get("created_at", datetime.now().isoformat()),
            "updated_at": frontmatter.get("updated_at", datetime.now().isoformat()),
            "content": body,
            "raw": raw,
            "file_path": file_path
        }
    except Exception as e:
        print(f"[Vault Parse Error on {file_path}]: {e}")
        return None

def save_note_to_vault(
    content: str,
    title: Optional[str] = None,
    source_book: str = "",
    category: str = "General",
    tags: Optional[List[str]] = None
) -> Dict[str, Any]:
    now = datetime.now()
    timestamp_str = now.strftime("%Y%m%d-%H%M%S")
    note_id = f"note-{timestamp_str}"
    
    # Auto-generate title if missing
    if not title or not title.strip():
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        first_line = lines[0] if lines else "Ghi chú không tiêu đề"
        title = re.sub(r'^[#\-\*\s]+', '', first_line)[:50].strip() or f"Ghi chú {now.strftime('%d/%m/%Y %H:%M')}"
        
    # Extract tags and wikilinks from content
    extracted_tags = extract_hashtags(content)
    all_tags = list(set((tags or []) + extracted_tags))
    
    extracted_links = extract_wikilinks(content)
    
    # Clean filename
    clean_filename = re.sub(r'[\\/*?:"<>|]', '_', title)[:40].strip() or note_id
    file_path = os.path.join(NOTES_DIR, f"{clean_filename}.md")
    
    # Handle filename collisions
    idx = 1
    while os.path.exists(file_path):
        file_path = os.path.join(NOTES_DIR, f"{clean_filename}_{idx}.md")
        idx += 1
        
    frontmatter = {
        "id": note_id,
        "title": title,
        "source_book": source_book,
        "category": category,
        "tags": all_tags,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "related_nodes": [f"[[{l}]]" for l in extracted_links]
    }
    
    file_content = f"---\n{yaml.dump(frontmatter, allow_unicode=True, default_flow_style=False)}---\n\n# {title}\n\n{content.strip()}\n"
    
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(file_content)
        
    # Upsert into SQLite Index
    upsert_note_index(
        note_id=note_id,
        title=title,
        file_path=file_path,
        source_book=source_book,
        category=category,
        content_raw=content.strip(),
        tags=all_tags,
        links=extracted_links,
        created_at=now.isoformat(),
        updated_at=now.isoformat()
    )
    
    return {
        "id": note_id,
        "title": title,
        "file_path": file_path,
        "tags": all_tags,
        "links": extracted_links,
        "created_at": now.strftime("%d/%m/%Y %H:%M:%S")
    }

def get_graph_data() -> Dict[str, Any]:
    # Fetch all nodes and edges for Web 3D Force Graph
    notes = get_all_notes_db(limit=500)
    edges = get_graph_edges()
    
    node_set = set()
    nodes = []
    
    for n in notes:
        node_set.add(n["title"])
        nodes.append({
            "id": n["title"],
            "name": n["title"],
            "group": n.get("category", "Note"),
            "val": 5,
            "book": n.get("source_book", ""),
            "note_id": n["id"]
        })
        if n.get("source_book") and n["source_book"] not in node_set:
            node_set.add(n["source_book"])
            nodes.append({
                "id": n["source_book"],
                "name": n["source_book"],
                "group": "Book",
                "val": 8,
                "book": "",
                "note_id": ""
            })
            
    links = []
    for e in edges:
        # Ensure both endpoints exist in nodes list
        if e["source_node"] not in node_set:
            node_set.add(e["source_node"])
            nodes.append({"id": e["source_node"], "name": e["source_node"], "group": "Concept", "val": 3, "book": "", "note_id": ""})
        if e["target_node"] not in node_set:
            node_set.add(e["target_node"])
            nodes.append({"id": e["target_node"], "name": e["target_node"], "group": "Concept", "val": 3, "book": "", "note_id": ""})
            
        links.append({
            "source": e["source_node"],
            "target": e["target_node"],
            "type": e.get("link_type", "related")
        })
        
    return {"nodes": nodes, "links": links}

def render_ascii_graph(topic: Optional[str] = None) -> str:
    edges = get_graph_edges()
    notes = get_all_notes_db(limit=50)
    
    if not edges and not notes:
        return "=== SƠ ĐỒ ĐỒ THỊ TRI THỨC (KNOWLEDGE GRAPH) ===\nChưa có ghi chú nào trong Vault. Hãy dùng lệnh `#note <nội dung>` để lưu ghi chú đầu tiên!\n================================================"

    res = [
        "=== SƠ ĐỒ ĐỒ THỊ TRI THỨC (KNOWLEDGE GRAPH) ===",
        f"Tổng số Ghi chú: {len(notes)} | Liên kết mạng lưới: {len(edges)}",
        "------------------------------------------------"
    ]
    
    if topic and topic.strip():
        top_clean = topic.strip().lower()
        matched_edges = [e for e in edges if top_clean in e["source_node"].lower() or top_clean in e["target_node"].lower()]
        if matched_edges:
            res.append(f"CÁC MỐI LIÊN KẾT LIÊN QUAN ĐẾN '{topic.upper()}':")
            for e in matched_edges[:15]:
                res.append(f"• [{e['source_node']}] ───({e['link_type']})───► [[{e['target_node']}]]")
        else:
            res.append(f"Chưa tìm thấy liên kết trực tiếp cho chủ đề '{topic}'.")
    else:
        # Show general cluster connections
        if edges:
            res.append("MẠNG LƯỚI LIÊN KẾT GẦN ĐÂY:")
            for e in edges[:12]:
                res.append(f"• [{e['source_node']}] ───({e['link_type']})───► [[{e['target_node']}]]")
        else:
            res.append("DANH SÁCH GHI CHÚ GẦN ĐÂY:")
            for n in notes[:8]:
                res.append(f"• [[{n['title']}]] (Nguồn: {n['source_book'] or 'Ý tưởng cá nhân'})")
                
    res.append("------------------------------------------------")
    res.append("Mẹo: Dùng `#node <tên>` để xem chi tiết 1 khái niệm, hoặc `#note` để ghi chép.")
    res.append("================================================")
    return "\n".join(res)

def get_node_details(node_name: str) -> str:
    edges = get_graph_edges()
    name_clean = node_name.strip()
    
    inbound = [e["source_node"] for e in edges if e["target_node"].lower() == name_clean.lower()]
    outbound = [e["target_node"] for e in edges if e["source_node"].lower() == name_clean.lower()]
    
    # Look up note content
    notes = search_notes_fts(name_clean, limit=1)
    note_content = notes[0]["content_raw"] if notes else "Chưa có nội dung ghi chú chi tiết."
    
    res = [
        f"=== CHI TIẾT KHÁI NIỆM: [[{name_clean.upper()}]] ===",
        f"Nội dung tóm tắt:\n{note_content[:300]}...",
        "------------------------------------------------",
        f"• Liên kết Đến (Inbound): {', '.join(inbound) if inbound else 'Không có'}",
        f"• Liên kết Đi (Outbound): {', '.join(outbound) if outbound else 'Không có'}",
        "================================================"
    ]
    return "\n".join(res)
