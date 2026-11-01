import asyncio
from datetime import datetime

from app import scheduler


def test_daily_digest_uses_current_year_and_is_idempotent(monkeypatch):
    captured = {"queries": [], "saved": []}
    now = datetime(2027, 1, 2, 7, 0, tzinfo=scheduler.VIETNAM_TZ)

    monkeypatch.setattr(scheduler, "current_time", lambda: now)
    monkeypatch.setattr(scheduler, "get_note_by_title", lambda title: None)

    async def fake_search(query, max_results):
        captured["queries"].append(query)
        return []

    monkeypatch.setattr(scheduler, "web_search", fake_search)
    monkeypatch.setattr(scheduler, "save_note_to_vault", lambda **kwargs: captured["saved"].append(kwargs))

    assert asyncio.run(scheduler.job_daily_morning_intel()) == "created"
    assert all("2027" in query for query in captured["queries"])
    assert captured["saved"][0]["title"] == "Daily Intel 2027-01-02"

    monkeypatch.setattr(scheduler, "get_note_by_title", lambda title: {"id": "existing"})
    assert asyncio.run(scheduler.job_daily_morning_intel()) == "already_exists"
    assert len(captured["saved"]) == 1


def test_scheduler_rejects_overlapping_run():
    lock = scheduler._job_locks["daily_morning_intel"]
    lock.acquire()
    try:
        assert asyncio.run(scheduler.job_daily_morning_intel()) == "already_running"
    finally:
        lock.release()


def test_manual_scheduler_rejects_unknown_job():
    result = asyncio.run(scheduler.trigger_job_manual("run_shell"))
    assert "Không tìm thấy" in result
