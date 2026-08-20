import os
import re
import yaml
import io
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

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
    matches = re.findall(r'\[\[([^\]\|]+)(?:\|[^\]]+)?\]\]', content)
    return [m.strip() for m in matches if m.strip()]

def extract_hashtags(content: str) -> List[str]:
    matches = re.findall(r'(?:^|\s)#([a-zA-Z0-9_\-]+)', content)
    return [m.strip().lower() for m in matches if m.strip()]

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
    
    if not title or not title.strip():
        lines = [l.strip() for l in content.splitlines() if l.strip()]
        first_line = lines[0] if lines else "Ghi chú không tiêu đề"
        title = re.sub(r'^[#\-\*\s]+', '', first_line)[:40].strip() or f"Ghi chú {now.strftime('%d/%m/%Y %H:%M')}"
        
    extracted_tags = extract_hashtags(content)
    all_tags = list(set((tags or []) + extracted_tags))
    extracted_links = extract_wikilinks(content)
    
    clean_filename = re.sub(r'[\\/*?:"<>|]', '_', title)[:35].strip() or note_id
    file_path = os.path.join(NOTES_DIR, f"{clean_filename}.md")
    
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
    """
    Kindle E-ink Optimized Vertical Knowledge Card Layout.
    Strictly constrained to 36-38 characters to prevent wrapping distortion on 6-inch screens.
    """
    notes = get_all_notes_db(limit=30)
    edges = get_graph_edges()
    
    if not notes:
        return (
            "=== SƠ ĐỒ ĐỒ THỊ TRI THỨC (VAULT) ===\n"
            "Chưa có ghi chú nào trong Vault.\n"
            "Dùng lệnh `#note <nội dung>` để lưu\n"
            "ghi chú đầu tiên!\n"
            "====================================="
        )

    # Group notes by Source Book
    book_groups: Dict[str, List[Dict[str, Any]]] = {}
    for n in notes:
        book = n.get("source_book") or "Ý tưởng cá nhân"
        book_groups.setdefault(book, []).append(n)
        
    out = [
        "=== ĐỒ THỊ TRI THỨC (KNOWLEDGE GRAPH) ===",
        f"Tổng: {len(notes)} ghi chú | {len(edges)} liên kết mạng",
        ""
    ]
    
    for book, b_notes in list(book_groups.items())[:4]:
        # Truncate book title cleanly
        b_title = book[:30] + "..." if len(book) > 30 else book
        out.append(f"┌─ 📚 {b_title}")
        
        for idx, n in enumerate(b_notes[:3]):
            is_last_note = (idx == len(b_notes) - 1 or idx == 2)
            prefix = "└─" if is_last_note else "├─"
            n_title = n['title'][:25]
            out.append(f"{prefix} 💡 [[{n_title}]]")
            
            # Find outbound links for this note
            node_links = [e['target_node'] for e in edges if e['source_node'] == n['title']]
            for l in node_links[:2]:
                l_clean = l[:20]
                out.append(f"│   └──► [[{l_clean}]]")
        out.append("")

    out.append("-------------------------------------")
    out.append("• Mẹo: Gõ `#node <tên>` xem 2 chiều.")
    out.append("• Xem ảnh nét: /v1/vault/graph/image")
    out.append("=====================================")
    return "\n".join(out)

def get_node_details(node_name: str) -> str:
    edges = get_graph_edges()
    name_clean = node_name.strip()
    
    inbound = [e["source_node"] for e in edges if e["target_node"].lower() == name_clean.lower()]
    outbound = [e["target_node"] for e in edges if e["source_node"].lower() == name_clean.lower()]
    
    notes = search_notes_fts(name_clean, limit=1)
    note_content = notes[0]["content_raw"] if notes else "Chưa có nội dung ghi chú chi tiết."
    
    res = [
        f"=== KHÁI NIỆM: [[{name_clean.upper()[:25]}]] ===",
        f"Trích dẫn / Ý tưởng:\n{note_content[:180]}...",
        "-------------------------------------",
        f"• Liên kết Đến (Inbound):\n  {', '.join(inbound[:3]) if inbound else 'Không có'}",
        f"• Liên kết Đi (Outbound):\n  {', '.join(outbound[:3]) if outbound else 'Không có'}",
        "====================================="
    ]
    return "\n".join(res)

def generate_kindle_graph_image() -> bytes:
    """
    Generate a high-contrast 300 DPI Black & White portrait image (750x1000)
    specifically designed for Kindle Paperwhite 6-inch E-ink display.
    """
    width, height = 750, 1000
    image = Image.new("L", (width, height), color=255) # 8-bit grayscale, pure white background
    draw = ImageDraw.Draw(image)
    
    # Try loading system font, fallback to default
    try:
        font_title = ImageFont.truetype("arial.ttf", 24)
        font_box = ImageFont.truetype("arial.ttf", 18)
        font_sub = ImageFont.truetype("arial.ttf", 14)
    except Exception:
        font_title = ImageFont.load_default()
        font_box = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    # Draw Header
    draw.rectangle([(20, 20), (width - 20, 70)], fill=0) # Black header bar
    draw.text((40, 32), "KINDLE KNOWLEDGE GRAPH (300 PPI)", fill=255, font=font_title)
    
    notes = get_all_notes_db(limit=8)
    edges = get_graph_edges()
    
    # Group into vertical tree cards
    y_offset = 100
    for idx, n in enumerate(notes[:5]):
        card_top = y_offset
        card_bottom = y_offset + 130
        
        # Outer Card Box
        draw.rounded_rectangle([(30, card_top), (width - 30, card_bottom)], radius=12, outline=0, width=3)
        
        # Book badge
        book_title = n.get("source_book") or "Ghi chép ý tưởng"
        draw.text((50, card_top + 15), f"BOOK: {book_title[:45]}", fill=0, font=font_sub)
        
        # Note Node Box (Inner pill)
        draw.rounded_rectangle([(50, card_top + 42), (width - 50, card_top + 80)], radius=8, fill=230, outline=0, width=2)
        draw.text((65, card_top + 50), f"[[{n['title'][:40]}]]", fill=0, font=font_box)
        
        # Cross links
        related = [e['target_node'] for e in edges if e['source_node'] == n['title']]
        if related:
            draw.text((70, card_top + 95), f"--> Connects to: [[{', '.join(related[:2])}]]", fill=80, font=font_sub)
        else:
            draw.text((70, card_top + 95), f"Tags: {', '.join(n.get('tags', [])[:3]) or 'General'}", fill=80, font=font_sub)

        # Draw vertical flow arrow to next card
        if idx < len(notes[:5]) - 1:
            draw.line([(width // 2, card_bottom), (width // 2, card_bottom + 30)], fill=0, width=3)
            draw.polygon([
                (width // 2, card_bottom + 30),
                (width // 2 - 8, card_bottom + 18),
                (width // 2 + 8, card_bottom + 18)
            ], fill=0)

        y_offset += 165
        if y_offset > height - 120:
            break

    # Output to PNG bytes
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf.getvalue()
