import os
import re
import urllib.parse
import xml.sax.saxutils as saxutils
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request, Response
from fastapi.responses import FileResponse, HTMLResponse, Response, StreamingResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db import (
    get_library_config,
    get_library_item,
    get_library_items_by_series,
    get_library_series,
    get_library_stats,
    search_library_items,
    set_library_config,
    update_library_cached_path,
    upsert_library_items,
)

router = APIRouter(tags=["Cloud Library & OPDS"])

CACHE_DIR = Path(settings.DATA_DIR) / "library_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
PAGE_CACHE_DIR = CACHE_DIR / "pages"
PAGE_CACHE_DIR.mkdir(parents=True, exist_ok=True)

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)


def _get_or_download_pdf(file_id: str) -> Path:
    """
    Ensure the PDF file is cached locally on server disk.
    Returns Path to the cached PDF. Raises HTTPException if not found or unreachable.
    """
    item = get_library_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy tập truyện trong thư viện")

    filename = item["name"]
    cached_file = CACHE_DIR / f"{file_id}_{filename}"

    if not cached_file.exists():
        cookies_file = Path(settings.DATA_DIR) / "google_cookies.txt"
        cookies_arg = str(cookies_file) if cookies_file.exists() else None
        try:
            import gdown
            downloaded = gdown.download(
                id=file_id,
                output=str(cached_file),
                quiet=True,
                cookies=cookies_arg,
                use_cookies=True if cookies_arg else False
            )
            if downloaded and Path(downloaded).exists():
                update_library_cached_path(file_id, str(cached_file))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"Lỗi khi tải file từ Google Drive: {str(e)[:100]}")

    if not cached_file.exists():
        raise HTTPException(status_code=502, detail="File chưa sẵn sàng trên máy chủ.")

    return cached_file


def escape_xml(text: str) -> str:
    return saxutils.escape(str(text or ""))


def get_mime_type(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return "application/pdf"
    elif ext in (".cbz", ".zip"):
        return "application/x-cbz"
    elif ext == ".cbr":
        return "application/x-cbr"
    elif ext == ".epub":
        return "application/epub+zip"
    elif ext == ".mobi":
        return "application/x-mobipocket-ebook"
    return "application/octet-stream"


# ============================================================================
# OPDS 1.2 Catalog Feeds for KOReader
# ============================================================================

@router.get("/opds", response_class=Response)
@router.get("/opds/catalog.xml", response_class=Response)
def get_opds_root(request: Request):
    """
    OPDS 1.2 Root Navigation Catalog for KOReader.
    """
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    stats = get_library_stats()

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opds="http://opds-spec.org/2010/catalog">
  <id>{base_url}/opds</id>
  <title>Thư Viện Truyện Tranh &amp; Sách Kindle (Cloud Drive)</title>
  <subtitle>Duyệt và tải truyện trực tiếp từ Google Drive vào Kindle — Tiết kiệm bộ nhớ máy</subtitle>
  <updated>{now}</updated>
  <author>
    <name>Kindle AI Gateway</name>
    <uri>{base_url}</uri>
  </author>
  <link rel="self" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  <link rel="start" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  <link rel="search" href="{base_url}/opds/search?q={{searchTerms}}" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />

  <!-- Navigation Entries -->
  <entry>
    <id>{base_url}/opds/series</id>
    <title>📁 Danh Mục Các Bộ Truyện ({stats['total_series']} bộ)</title>
    <updated>{now}</updated>
    <content type="text">Duyệt theo từng bộ truyện tranh, tiểu thuyết và tài liệu PDF.</content>
    <link rel="subsection" href="{base_url}/opds/series" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  </entry>

  <entry>
    <id>{base_url}/opds/all</id>
    <title>📚 Tất Cả Tập Truyện &amp; Tài Liệu ({stats['total_items']} tập)</title>
    <updated>{now}</updated>
    <content type="text">Danh sách toàn bộ các tập truyện có thể tải về đọc ngay.</content>
    <link rel="subsection" href="{base_url}/opds/all" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />
  </entry>
</feed>"""
    return Response(content=xml, media_type="application/atom+xml;profile=opds-catalog;kind=navigation")


@router.get("/opds/series", response_class=Response)
def get_opds_series_list(request: Request):
    """
    OPDS feed listing all manga / book series folders.
    """
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    series_list = get_library_series()

    entries_xml = []
    for s in series_list:
        series_name = s["series"]
        count = s["count"]
        encoded_name = urllib.parse.quote(series_name)
        entries_xml.append(f"""  <entry>
    <id>{base_url}/opds/series/{encoded_name}</id>
    <title>{escape_xml(series_name)} ({count} tập)</title>
    <updated>{now}</updated>
    <content type="text">Trọn bộ {count} tập / chương.</content>
    <link rel="subsection" href="{base_url}/opds/series/{encoded_name}" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />
  </entry>""")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opds="http://opds-spec.org/2010/catalog">
  <id>{base_url}/opds/series</id>
  <title>Danh Mục Các Bộ Truyện</title>
  <updated>{now}</updated>
  <link rel="self" href="{base_url}/opds/series" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  <link rel="up" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  <link rel="start" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />

{''.join(entries_xml)}
</feed>"""
    return Response(content=xml, media_type="application/atom+xml;profile=opds-catalog;kind=navigation")


@router.get("/opds/series/{series_name}", response_class=Response)
def get_opds_series_items(series_name: str, request: Request):
    """
    OPDS acquisition feed containing all volumes of a specific series.
    """
    series_name = urllib.parse.unquote(series_name)
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = get_library_items_by_series(series_name)

    entries_xml = []
    for item in items:
        mime = item.get("mime_type") or get_mime_type(item["name"])
        size_str = f"({item['size_bytes'] // 1024 // 1024} MB)" if item.get("size_bytes") else ""
        entries_xml.append(f"""  <entry>
    <id>{base_url}/api/v1/library/download/{item['id']}</id>
    <title>{escape_xml(item['name'])}</title>
    <updated>{now}</updated>
    <content type="text">{escape_xml(series_name)} {size_str}</content>
    <link rel="http://opds-spec.org/acquisition" href="{base_url}/api/v1/library/download/{item['id']}" type="{mime}" />
  </entry>""")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opds="http://opds-spec.org/2010/catalog">
  <id>{base_url}/opds/series/{urllib.parse.quote(series_name)}</id>
  <title>{escape_xml(series_name)}</title>
  <updated>{now}</updated>
  <link rel="self" href="{base_url}/opds/series/{urllib.parse.quote(series_name)}" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />
  <link rel="up" href="{base_url}/opds/series" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  <link rel="start" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />

{''.join(entries_xml)}
</feed>"""
    return Response(content=xml, media_type="application/atom+xml;profile=opds-catalog;kind=acquisition")


@router.get("/opds/all", response_class=Response)
def get_opds_all_items(request: Request, limit: int = 200):
    """
    OPDS acquisition feed of all items.
    """
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = search_library_items("", limit=limit)

    entries_xml = []
    for item in items:
        mime = item.get("mime_type") or get_mime_type(item["name"])
        entries_xml.append(f"""  <entry>
    <id>{base_url}/api/v1/library/download/{item['id']}</id>
    <title>{escape_xml(item['name'])}</title>
    <updated>{now}</updated>
    <content type="text">{escape_xml(item['series'])}</content>
    <link rel="http://opds-spec.org/acquisition" href="{base_url}/api/v1/library/download/{item['id']}" type="{mime}" />
  </entry>""")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opds="http://opds-spec.org/2010/catalog">
  <id>{base_url}/opds/all</id>
  <title>Tất Cả Sách &amp; Truyện</title>
  <updated>{now}</updated>
  <link rel="self" href="{base_url}/opds/all" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />
  <link rel="up" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />
  <link rel="start" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />

{''.join(entries_xml)}
</feed>"""
    return Response(content=xml, media_type="application/atom+xml;profile=opds-catalog;kind=acquisition")


@router.get("/opds/search", response_class=Response)
def get_opds_search(q: str = Query(default="", alias="q"), request: Request = None):
    """
    OPDS search query endpoint.
    """
    base_url = str(request.base_url).rstrip("/")
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    items = search_library_items(q, limit=100) if q else []

    entries_xml = []
    for item in items:
        mime = item.get("mime_type") or get_mime_type(item["name"])
        entries_xml.append(f"""  <entry>
    <id>{base_url}/api/v1/library/download/{item['id']}</id>
    <title>{escape_xml(item['name'])}</title>
    <updated>{now}</updated>
    <content type="text">{escape_xml(item['series'])}</content>
    <link rel="http://opds-spec.org/acquisition" href="{base_url}/api/v1/library/download/{item['id']}" type="{mime}" />
  </entry>""")

    xml = f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:opds="http://opds-spec.org/2010/catalog">
  <id>{base_url}/opds/search?q={urllib.parse.quote(q)}</id>
  <title>Kết quả tìm kiếm cho: {escape_xml(q)}</title>
  <updated>{now}</updated>
  <link rel="self" href="{base_url}/opds/search?q={urllib.parse.quote(q)}" type="application/atom+xml;profile=opds-catalog;kind=acquisition" />
  <link rel="up" href="{base_url}/opds" type="application/atom+xml;profile=opds-catalog;kind=navigation" />

{''.join(entries_xml)}
</feed>"""
    return Response(content=xml, media_type="application/atom+xml;profile=opds-catalog;kind=acquisition")


# ============================================================================
# File Download & Streaming Endpoint with Cache
# ============================================================================

@router.get("/api/v1/library/download/{file_id}")
async def download_library_file(file_id: str, request: Request):
    """
    Downloads / streams file to KOReader on Kindle with HTTP Range support.
    Cached on server disk for instant re-download.
    """
    item = get_library_item(file_id)
    if not item:
        raise HTTPException(404, "Không tìm thấy file trong danh mục thư viện")

    filename = item["name"]
    mime_type = item.get("mime_type") or get_mime_type(filename)
    cached_file = CACHE_DIR / f"{file_id}_{filename}"

    # 1. If not cached, attempt to fetch from Google Drive via gdown / direct URL
    if not cached_file.exists():
        cookies_file = Path(settings.DATA_DIR) / "google_cookies.txt"
        cookies_arg = str(cookies_file) if cookies_file.exists() else None

        try:
            import gdown
            downloaded = gdown.download(
                id=file_id,
                output=str(cached_file),
                quiet=True,
                cookies=cookies_arg,
                use_cookies=True if cookies_arg else False
            )
            if downloaded and Path(downloaded).exists():
                update_library_cached_path(file_id, str(cached_file))
            else:
                # Fallback to direct streaming from Google Drive
                direct_url = f"https://drive.google.com/uc?id={file_id}&export=download"
                return Response(
                    status_code=307,
                    headers={"Location": direct_url}
                )
        except Exception as e:
            # If download fails due to quota limit without cookies, redirect directly
            direct_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            return Response(
                status_code=307,
                headers={"Location": direct_url}
            )

    if not cached_file.exists():
        raise HTTPException(502, "Không thể tải file từ Google Drive. Vui lòng kiểm tra quyền truy cập hoặc cấu hình cookies.")

    # 2. Return file with HTTP Range support (for KOReader download resumption)
    return FileResponse(
        path=str(cached_file),
        media_type=mime_type,
        filename=filename,
        content_disposition_type="attachment"
    )


# ============================================================================
# E-ink Web Reader & Library Portal
# ============================================================================

@router.get("/library", response_class=HTMLResponse)
def web_library_portal(request: Request, q: Optional[str] = None, series: Optional[str] = None):
    """
    Clean, high-contrast, black-and-white E-ink friendly web library portal.
    Open directly on Kindle's built-in web browser or phone!
    """
    stats = get_library_stats()
    all_series = get_library_series()

    if q:
        items = search_library_items(q, limit=100)
        current_view = f"Tìm kiếm: {q}"
    elif series:
        items = get_library_items_by_series(series)
        current_view = series
    else:
        items = []
        current_view = "Chọn một bộ truyện để xem danh sách tập"

    return templates.TemplateResponse(
        request=request,
        name="library.html",
        context={
            "stats": stats,
            "all_series": all_series,
            "items": items,
            "current_series": series,
            "current_view": current_view,
            "q": q or "",
        }
    )


@router.get("/library/read/{file_id}", response_class=HTMLResponse)
def web_reader(request: Request, file_id: str, page: int = Query(1, ge=1)):
    """
    Dedicated minimalist E-ink web reader interface for Kindle browser.
    """
    item = get_library_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy tập truyện")

    return templates.TemplateResponse(
        request=request,
        name="reader.html",
        context={
            "item": item,
            "file_id": file_id,
            "initial_page": page,
        }
    )


@router.get("/api/v1/library/info/{file_id}")
def get_book_info(file_id: str):
    """
    Returns book metadata and total page count by inspecting the PDF file.
    """
    item = get_library_item(file_id)
    if not item:
        raise HTTPException(status_code=404, detail="Không tìm thấy tập truyện")

    pdf_path = _get_or_download_pdf(file_id)

    try:
        import fitz
        doc = fitz.open(str(pdf_path))
        page_count = len(doc)
        doc.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Không thể đọc file PDF: {str(e)}")

    return {
        "id": file_id,
        "name": item["name"],
        "series": item.get("series", ""),
        "total_pages": page_count,
    }


@router.get("/api/v1/library/page/{file_id}/{page_num}")
def get_rendered_page(
    file_id: str,
    page_num: int,
    max_w: int = Query(1072, ge=200, le=2400),
    max_h: int = Query(1448, ge=200, le=3200),
    quality: int = Query(80, ge=30, le=100)
):
    """
    Renders a specific PDF page to an E-ink Carta optimized grayscale JPEG.
    Caches rendered JPEG on server disk for sub-5ms repeat loads.
    """
    if page_num < 1:
        raise HTTPException(status_code=400, detail="Trang phải lớn hơn hoặc bằng 1")

    # Check cache first
    book_cache_dir = PAGE_CACHE_DIR / file_id
    cached_page_file = book_cache_dir / f"p_{page_num}_{max_w}x{max_h}_q{quality}.jpg"

    if cached_page_file.exists():
        return FileResponse(
            path=str(cached_page_file),
            media_type="image/jpeg",
            headers={"Cache-Control": "public, max-age=604800"}  # Cache 7 days
        )

    # Need source PDF
    pdf_path = _get_or_download_pdf(file_id)

    import fitz
    doc = fitz.open(str(pdf_path))
    try:
        if page_num > len(doc):
            raise HTTPException(status_code=404, detail=f"Trang {page_num} vượt quá tổng số trang ({len(doc)})")

        page = doc[page_num - 1]

        # Calculate optimal scale factor fitting Kindle E-ink resolution
        rect = page.rect
        scale_x = max_w / rect.width if rect.width > 0 else 1.0
        scale_y = max_h / rect.height if rect.height > 0 else 1.0
        scale = min(scale_x, scale_y)

        # Render grayscale pixmap
        pix = page.get_pixmap(
            matrix=fitz.Matrix(scale, scale),
            colorspace=fitz.csGRAY,
            alpha=False
        )
        img_bytes = pix.tobytes("jpeg", jpg_quality=quality)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi hiển thị trang: {str(e)}")
    finally:
        try:
            doc.close()
        except Exception:
            pass

    # Save to disk cache
    book_cache_dir.mkdir(parents=True, exist_ok=True)
    cached_page_file.write_bytes(img_bytes)

    return Response(
        content=img_bytes,
        media_type="image/jpeg",
        headers={"Cache-Control": "public, max-age=604800"}
    )


# ============================================================================
# Background Sync Task for Google Drive Folder
# ============================================================================

def background_sync_drive():
    """
    Background worker that crawls Google Drive folder and indexes files.
    """
    root_folder_id = get_library_config("root_folder_id", "1eEWmqXZZmDXx4QsmsTsnjkgUMp7pe6EH")
    set_library_config("sync_status", "syncing")

    try:
        import gdown
        files = gdown.download_folder(id=root_folder_id, skip_download=True, remaining_ok=True, quiet=True)
        if not files:
            set_library_config("sync_status", "error: no files found")
            return

        items_to_insert = []
        for f in files:
            file_id = f.id
            rel_path = f.path.replace("\\", "/").strip("/")
            parts = rel_path.split("/")
            file_name = parts[-1]
            series_name = parts[0] if len(parts) > 1 else "Tổng Hợp"

            ext = os.path.splitext(file_name)[1].lower()
            if ext in (".pdf", ".cbz", ".cbr", ".epub", ".zip", ".mobi"):
                items_to_insert.append({
                    "id": file_id,
                    "name": file_name,
                    "series": series_name,
                    "folder_path": rel_path,
                    "file_ext": ext,
                    "mime_type": get_mime_type(file_name),
                    "size_bytes": 0,
                })

        count = upsert_library_items(items_to_insert)
        now_str = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M:%S UTC")
        set_library_config("last_synced_at", now_str)
        set_library_config("sync_status", "completed")
        set_library_config("total_indexed", str(count))
    except Exception as e:
        set_library_config("sync_status", f"error: {str(e)[:100]}")
