import threading
from datetime import datetime
from zoneinfo import ZoneInfo

from app.db import get_note_by_title
from app.search import format_search_results, web_search
from app.vault import get_all_notes_db, save_note_to_vault

VIETNAM_TZ = ZoneInfo("Asia/Ho_Chi_Minh")
_job_locks = {
    "daily_morning_intel": threading.Lock(),
    "weekly_reading_retro": threading.Lock(),
}

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler

    scheduler = AsyncIOScheduler(timezone=VIETNAM_TZ)
except ImportError:
    scheduler = None


def current_time() -> datetime:
    return datetime.now(VIETNAM_TZ)


async def job_daily_morning_intel() -> str:
    lock = _job_locks["daily_morning_intel"]
    if not lock.acquire(blocking=False):
        return "already_running"
    try:
        now = current_time()
        title = f"Daily Intel {now:%Y-%m-%d}"
        if get_note_by_title(title):
            return "already_exists"

        queries = [
            f"AI technology breakthroughs and product updates {now.year}",
            f"Tech market trends and venture funding updates {now.year}",
        ]
        results = []
        for query in queries:
            results.extend(await web_search(query, max_results=3) or [])

        content = "\n".join([
            f"=== DAILY MORNING INTEL - NGÀY {now:%d/%m/%Y} ===",
            f"Tổng hợp tự động lúc {now:%H:%M:%S} (Asia/Ho_Chi_Minh)",
            "",
            "## 1. Tin tức và bước ngoặt công nghệ đáng chú ý",
            format_search_results(results) if results else "Không có dữ liệu mới.",
            "",
            "## 2. Gợi ý định hướng trong ngày",
            "- Rà soát các mục tiêu ưu tiên cao nhất trong ngày.",
            "- Đối chiếu insight công nghệ mới với lộ trình sản phẩm hiện tại.",
        ])
        save_note_to_vault(content=content, title=title, category="Daily Digest",
                           tags=["daily-digest", "market-intel", "ai-trends"])
        return "created"
    finally:
        lock.release()


async def job_weekly_retro() -> str:
    lock = _job_locks["weekly_reading_retro"]
    if not lock.acquire(blocking=False):
        return "already_running"
    try:
        now = current_time()
        week = now.strftime("%G-W%V")
        title = f"Weekly Retro {week}"
        if get_note_by_title(title):
            return "already_exists"

        notes = get_all_notes_db(limit=20)
        lines = [
            f"=== BÁO CÁO TỔNG KẾT TUẦN - {week} ===",
            f"Tổng hợp kiến thức đến {now:%d/%m/%Y %H:%M}:",
            "",
            "## 1. Ghi chú và khái niệm đã thu nạp",
        ]
        if notes:
            for note in notes[:10]:
                source = note.get("source_book") or "Ghi chép tự do"
                lines.append(f"- [[{note['title']}]] (Nguồn: {source})")
        else:
            lines.append("- Chưa có ghi chú mới trong tuần.")
        lines.extend([
            "",
            "## 2. Phân tích xu hướng tư duy",
            "- Rà soát các chủ đề xuất hiện lặp lại trong ghi chú tuần này.",
            "- Chọn một khái niệm quan trọng để đào sâu và áp dụng trong tuần tới.",
        ])
        save_note_to_vault(content="\n".join(lines), title=title, category="Weekly Retro",
                           tags=["weekly-retro", "knowledge-audit"])
        return "created"
    finally:
        lock.release()


def start_scheduler() -> None:
    if not scheduler or scheduler.running:
        return
    common = {"replace_existing": True, "max_instances": 1, "coalesce": True, "misfire_grace_time": 900}
    scheduler.add_job(job_daily_morning_intel, "cron", hour=7, minute=0,
                      id="daily_morning_intel", **common)
    scheduler.add_job(job_weekly_retro, "cron", day_of_week="sun", hour=21, minute=0,
                      id="weekly_reading_retro", **common)
    scheduler.start()


def shutdown_scheduler() -> None:
    if scheduler and scheduler.running:
        scheduler.shutdown(wait=False)


async def trigger_job_manual(job_name: str) -> str:
    jobs = {
        "daily_morning_intel": (job_daily_morning_intel, "Daily Morning Intel"),
        "weekly_reading_retro": (job_weekly_retro, "Weekly Reading Retro"),
    }
    if job_name not in jobs:
        return f"Không tìm thấy tác vụ '{job_name}'."
    job, label = jobs[job_name]
    result = await job()
    messages = {
        "created": f"Đã chạy {label} và lưu vào Vault.",
        "already_exists": f"{label} đã tồn tại cho kỳ hiện tại; không tạo bản trùng.",
        "already_running": f"{label} đang chạy; yêu cầu trùng đã được bỏ qua.",
    }
    return messages[result]
