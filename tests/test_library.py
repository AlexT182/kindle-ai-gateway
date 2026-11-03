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
