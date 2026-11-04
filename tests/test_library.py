import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db import upsert_library_items, get_library_stats, get_library_series

client = TestClient(app)


def test_library_db_and_opds():
    items = [
        {
            "id": "test_bj_01",
            "name": "Bác Sĩ Quái Dị Vol 01.pdf",
            "series": "Bác Sĩ Quái Dị",
            "folder_path": "Truyện Tranh/Bác Sĩ Quái Dị/Vol 01.pdf",
            "file_ext": ".pdf",
            "mime_type": "application/pdf",
            "size_bytes": 25000000,
        },
        {
            "id": "test_7seeds_01",
            "name": "7 Seeds Vol 01.pdf",
            "series": "7 Seeds",
            "folder_path": "Truyện Tranh/7 Seeds/Vol 01.pdf",
            "file_ext": ".pdf",
            "mime_type": "application/pdf",
            "size_bytes": 30000000,
        }
    ]
    upsert_library_items(items)

    stats = get_library_stats()
    assert stats["total_items"] >= 2
    assert stats["total_series"] >= 2

    # OPDS root catalog test
    resp_root = client.get("/opds")
    assert resp_root.status_code == 200
    assert "application/atom+xml" in resp_root.headers.get("content-type", "")
    assert "Danh Mục Các Bộ Truyện" in resp_root.text

    # OPDS series list test
    resp_series = client.get("/opds/series")
    assert resp_series.status_code == 200
    assert "Bác Sĩ Quái Dị" in resp_series.text
    assert "7 Seeds" in resp_series.text

    # OPDS series items feed test
    resp_items = client.get("/opds/series/B%C3%A1c%20S%C4%A9%20Qu%C3%A1i%20D%E1%BB%8B")
    assert resp_items.status_code == 200
    assert "Bác Sĩ Quái Dị Vol 01.pdf" in resp_items.text
    assert "acquisition" in resp_items.text

    # Web Library portal test
    resp_web = client.get("/library")
    assert resp_web.status_code == 200
    assert "Thư Viện Kindle Cloud" in resp_web.text


def test_web_reader_and_page_render(tmp_path):
    import fitz
    from app.routes.library import CACHE_DIR, PAGE_CACHE_DIR

    # Create a small dummy 2-page PDF
    dummy_file_id = "test_mini_book_01"
    pdf_filename = f"{dummy_file_id}_Mini Manga.pdf"
    pdf_path = CACHE_DIR / pdf_filename

    doc = fitz.open()
    # Page 1: 400x600 with text
    page1 = doc.new_page(width=400, height=600)
    page1.insert_text((50, 100), "Trang 1 Manga Test", fontsize=20)
    # Page 2: 400x600 with text
    page2 = doc.new_page(width=400, height=600)
    page2.insert_text((50, 100), "Trang 2 Manga Test", fontsize=20)
    doc.save(str(pdf_path))
    doc.close()

    # Insert item into DB
    item = {
        "id": dummy_file_id,
        "name": "Mini Manga.pdf",
        "series": "Mini Manga Series",
        "folder_path": "Truyện Tranh/Mini Manga/Mini Manga.pdf",
        "file_ext": ".pdf",
        "mime_type": "application/pdf",
        "size_bytes": 10000,
    }
    upsert_library_items([item])

    # 1. Test Reader HTML route
    resp_reader = client.get(f"/library/read/{dummy_file_id}")
    assert resp_reader.status_code == 200
    assert "Mini Manga.pdf" in resp_reader.text
    assert "Kindle Web Reader" in resp_reader.text

    # 2. Test Book Info API
    resp_info = client.get(f"/api/v1/library/info/{dummy_file_id}")
    assert resp_info.status_code == 200
    info_json = resp_info.json()
    assert info_json["total_pages"] == 2
    assert info_json["name"] == "Mini Manga.pdf"

    # 3. Test Render Page 1 API
    resp_p1 = client.get(f"/api/v1/library/page/{dummy_file_id}/1?max_w=600&max_h=800")
    assert resp_p1.status_code == 200
    assert resp_p1.headers["content-type"] == "image/jpeg"
    assert len(resp_p1.content) > 100

    # 4. Test Render Page 2 API (Verify cache hit)
    resp_p2 = client.get(f"/api/v1/library/page/{dummy_file_id}/2?max_w=600&max_h=800")
    assert resp_p2.status_code == 200
    assert resp_p2.headers["content-type"] == "image/jpeg"

    # Verify cached file was written
    cached_file = PAGE_CACHE_DIR / dummy_file_id / "p_1_600x800_q80.jpg"
    assert cached_file.exists()

    # 5. Out of bounds page
    resp_err = client.get(f"/api/v1/library/page/{dummy_file_id}/99")
    assert resp_err.status_code == 404
