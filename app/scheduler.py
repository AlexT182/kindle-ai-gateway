import os
import asyncio
from datetime import datetime
from typing import Dict, Any, List
try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    scheduler = AsyncIOScheduler()
    HAS_APSCHEDULER = True
except ImportError:
    scheduler = None
    HAS_APSCHEDULER = False

async def job_daily_morning_intel():
    print("[Scheduler] Running Daily Morning Intel...")
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    
    queries = [
        "AI technology breakthroughs and product updates 2026",
        "Tech market trends and venture funding updates 2026"
    ]
    
    all_results = []
    for q in queries:
        res = await web_search(q, max_results=3)
        if res:
            all_results.extend(res)
            
    content_lines = [
        f"=== DAILY MORNING INTEL - NGÀY {date_str} ===",
        f"Tổng hợp tự động vào lúc {now.strftime('%H:%M:%S')} (GMT+7)",
        "",
        "## 1. Tin Tức & Bước Ngoặt Công Nghệ Đáng Chú Ý:",
        format_search_results(all_results) if all_results else "Không có dữ liệu mới.",
        "",
        "## 2. Gợi Ý Định Hướng Trong Ngày:",
        "- Rà soát lại các mục tiêu ưu tiên cao nhất trong ngày.",
        "- Đối chiếu các insight công nghệ mới với lộ trình sản phẩm hiện tại."
    ]
    
    save_note_to_vault(
        title=f"Daily Intel {now.strftime('%Y-%m-%d')}",
        content="\n".join(content_lines),
        category="Daily Digest",
        tags=["daily-digest", "market-intel", "ai-trends"]
    )
    print("[Scheduler] Daily Morning Intel completed and saved to Vault!")

async def job_weekly_retro():
    print("[Scheduler] Running Weekly Reading Retro...")
    now = datetime.now()
    week_str = now.strftime("%Y-W%W")
    
    notes = get_all_notes_db(limit=20)
    
    lines = [
        f"=== BÁO CÁO TỔNG KẾT TUẦN (WEEKLY RETROSPECTIVE) - {week_str} ===",
        f"Tổng hợp các ghi chú và tri thức đã thu nạp trong tuần tính đến {now.strftime('%d/%m/%Y %H:%M')}:",
        "",
        "## 1. Các Ghi Chú & Khái Niệm Đã Thu Nạp:"
    ]
    
    if notes:
        for n in notes[:10]:
            lines.append(f"- [[{n['title']}]] (Nguồn: {n.get('source_book') or 'Ghi chép tự do'})")
    else:
        lines.append("- Chưa có ghi chú mới trong tuần.")
        
    lines.extend([
        "",
        "## 2. Phân Tích Xu Hướng Tư Duy:",
        "- Trọng tâm tuần này hướng về tối ưu hóa quy trình, thiết kế sản phẩm và tư duy thực nghiệm.",
        "- Đề xuất tuần tới: Đào sâu thêm các Case Study triển khai thực tế."
    ])
    
    save_note_to_vault(
        title=f"Weekly Retro {week_str}",
        content="\n".join(lines),
        category="Weekly Retro",
        tags=["weekly-retro", "knowledge-audit"]
    )
    print("[Scheduler] Weekly Reading Retro completed and saved to Vault!")

def start_scheduler():
    if scheduler and not scheduler.running:
        # Schedule Daily Digest at 07:00 AM every day
        scheduler.add_job(
            job_daily_morning_intel,
            'cron',
            hour=7,
            minute=0,
            id='daily_morning_intel',
            replace_existing=True
        )
        # Schedule Weekly Retro every Sunday at 21:00
        scheduler.add_job(
            job_weekly_retro,
            'cron',
            day_of_week='sun',
            hour=21,
            minute=0,
            id='weekly_reading_retro',
            replace_existing=True
        )
        scheduler.start()
        print("[Scheduler] APScheduler started successfully!")
    else:
        print("[Scheduler] Running in standalone mode without APScheduler background loop.")

async def trigger_job_manual(job_name: str) -> str:
    if job_name == "daily_morning_intel":
        await job_daily_morning_intel()
        return "Đã thực thi thành công Daily Morning Intel và lưu vào Vault!"
    elif job_name == "weekly_reading_retro":
        await job_weekly_retro()
        return "Đã thực thi thành công Weekly Reading Retro và lưu vào Vault!"
    return f"Không tìm thấy tác vụ '{job_name}'."
