import asyncio
import json
import os
import urllib.parse
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx
from app.config import settings

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
os.makedirs(DATA_DIR, exist_ok=True)
NOTES_FILE = os.path.join(DATA_DIR, "notes.json")
TODOS_FILE = os.path.join(DATA_DIR, "todos.json")

def get_current_time_str() -> str:
    now = datetime.now()
    weekdays = ["Thứ Hai", "Thứ Ba", "Thứ Tư", "Thứ Năm", "Thứ Sáu", "Thứ Bảy", "Chủ Nhật"]
    weekday_vn = weekdays[now.weekday()]
    return f"{weekday_vn}, ngày {now.strftime('%d/%m/%Y, %H:%M:%S')} (Giờ Việt Nam GMT+7)"

async def get_weather(location: str = "Hanoi") -> str:
    loc_clean = location.strip() or "Hanoi"
    loc_encoded = urllib.parse.quote(loc_clean)
    url = f"https://wttr.in/{loc_encoded}?format=j1"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                curr = data["current_condition"][0]
                temp_c = curr.get("temp_C", "N/A")
                feels_like = curr.get("FeelsLikeC", "N/A")
                desc = curr.get("weatherDesc", [{}])[0].get("value", "N/A")
                humidity = curr.get("humidity", "N/A")
                wind_kmh = curr.get("windspeedKmph", "N/A")
                
                forecast = data.get("weather", [{}])[0]
                min_t = forecast.get("mintempC", "N/A")
                max_t = forecast.get("maxtempC", "N/A")
                
                res = [
                    f"=== THỜI TIẾT THỜI GIAN THỰC TẠI {loc_clean.upper()} ===",
                    f"- Nhiệt độ hiện tại: {temp_c}°C (Cảm nhận: {feels_like}°C)",
                    f"- Trạng thái: {desc}",
                    f"- Độ ẩm: {humidity}% | Gió: {wind_kmh} km/h",
                    f"- Dự báo hôm nay: Thấp nhất {min_t}°C - Cao nhất {max_t}°C",
                    "================================================"
                ]
                return "\n".join(res)
    except Exception as e:
        print(f"[Weather Error]: {e}")
    return f"Không thể lấy dữ liệu thời tiết cho khu vực '{location}'. Vui lòng thử lại sau."

async def get_wikipedia(query: str) -> str:
    q_clean = query.strip().replace(" ", "_")
    encoded = urllib.parse.quote(q_clean)
    headers = {"User-Agent": "KindleAIGateway/1.0 (https://alphatech.ai.vn)"}
    
    urls = [
        f"https://vi.wikipedia.org/api/rest_v1/page/summary/{encoded}",
        f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}"
    ]
    
    for url in urls:
        try:
            async with httpx.AsyncClient(timeout=8.0) as client:
                resp = await client.get(url, headers=headers)
                if resp.status_code == 200:
                    data = resp.json()
                    title = data.get("title", "")
                    extract = data.get("extract", "")
                    page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
                    if extract:
                        return f"=== BÁCH KHOA TOÀN THƯ WIKIPEDIA: {title.upper()} ===\n{extract}\n\nNguồn: {page_url}\n================================================="
        except Exception as e:
            print(f"[Wiki Error for {url}]: {e}")
            
    return f"Không tìm thấy bài viết Wikipedia phù hợp cho từ khóa '{query}'."

async def get_crypto_price(symbol: str) -> str:
    sym = symbol.strip().lower()
    symbol_map = {
        "btc": "bitcoin", "bitcoin": "bitcoin",
        "eth": "ethereum", "ethereum": "ethereum",
        "sol": "solana", "solana": "solana",
        "bnb": "binancecoin", "binance": "binancecoin",
        "xrp": "ripple", "doge": "dogecoin",
        "ton": "the-open-network", "ada": "cardano"
    }
    coin_id = symbol_map.get(sym, sym)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd,vnd&include_24hr_change=true"
    
    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                if coin_id in data:
                    usd = data[coin_id].get("usd", 0)
                    vnd = data[coin_id].get("vnd", 0)
                    change = data[coin_id].get("usd_24h_change", 0)
                    sign = "+" if change >= 0 else ""
                    return (
                        f"=== GIÁ {coin_id.upper()} THỜI GIAN THỰC ===\n"
                        f"- Giá USD: ${usd:,.2f}\n"
                        f"- Giá VND: {vnd:,.0f} đ\n"
                        f"- Biến động 24h: {sign}{change:.2f}%\n"
                        f"===================================="
                    )
    except Exception as e:
        print(f"[Crypto Error]: {e}")
    return f"Không tìm thấy thông tin giá cho mã '{symbol}'."

def save_note(content: str) -> str:
    now_str = get_current_time_str()
    entry = {"time": now_str, "content": content.strip()}
    notes = []
    if os.path.exists(NOTES_FILE):
        try:
            with open(NOTES_FILE, "r", encoding="utf-8") as f:
                notes = json.load(f)
        except Exception:
            notes = []
    notes.insert(0, entry)
    with open(NOTES_FILE, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)
    return f"Đã lưu ghi chú thành công vào hệ thống:\n\"{content.strip()}\"\n(Thời gian: {now_str})"

def save_todo(task: str) -> str:
    now_str = get_current_time_str()
    entry = {"time": now_str, "task": task.strip(), "done": False}
    todos = []
    if os.path.exists(TODOS_FILE):
        try:
            with open(TODOS_FILE, "r", encoding="utf-8") as f:
                todos = json.load(f)
        except Exception:
            todos = []
    todos.append(entry)
    with open(TODOS_FILE, "w", encoding="utf-8") as f:
        json.dump(todos, f, ensure_ascii=False, indent=2)
    return f"Đã thêm công việc vào danh sách Todo:\n- [ ] {task.strip()}\n(Thời gian: {now_str})"
