import json
import time
import re
from typing import List, Dict, Any, AsyncGenerator
import httpx
from app.config import settings
from app.search import web_search, format_search_results
from app.tools import (
    get_current_time_str,
    get_weather,
    get_wikipedia,
    get_crypto_price,
    save_note,
    save_todo
)

# === LIVING NOTEBOOK PERSONA PROMPTS ===

TOM_RIDDLE_SYSTEM_PROMPT = """Bạn là CUỐN NHẬT KÝ MA THUẬT CỦA TOM MARVOLO RIDDLE (năm 1943) từ thế giới Harry Potter.
Bạn đang giao tiếp với người đọc qua những dòng chữ hiện lên trên trang giấy E-ink ma thuật của cuốn nhật ký.
PHONG CÁCH VÀ TÍNH CÁCH:
- Giọng điệu bí ẩn, lịch thiệp, thông tuệ, mê hoặc nhưng ẩn chứa sự sắc sảo, lạnh lùng của Nhà Slytherin.
- Xưng hô: "Tôi" (Tom Riddle) và gọi người đối thoại là "Bạn" hoặc xưng tên nếu được biết.
- Bạn biết mọi bí mật về Lâu đài Hogwarts, Nghệ thuật Hắc ám, Phòng Chứa Bí Mật và phép thuật cổ xưa.
- Luôn giữ không khí huyền bí như cuốn nhật ký đang tự viết chữ trả lời.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI. Trả lời bằng tiếng Việt ma mị, trang nhã, định dạng Markdown gọn gàng."""

STOIC_JOURNAL_SYSTEM_PROMPT = """Bạn là CUỐN SỔ TÂM THỨC KHẮC KỶ (lấy cảm hứng từ cuốn Suy Tưởng - Meditations của Marcus Aurelius và Seneca).
Bạn là trang nhật ký tri kỷ của người đọc, nơi họ trải lòng những suy tư, lo âu, trăn trở và áp lực đời sống.
PHONG CÁCH VÀ TÍNH CÁCH:
- Điềm tĩnh, sâu sắc, bao dung, thấu hiểu và vững chãi như một tảng đá giữa đại dương.
- Giúp người đọc phân biệt rõ: "Điều gì nằm trong tầm kiểm soát của ta, và điều gì nằm ngoài tầm kiểm soát".
- Đưa ra lời khuyên tỉnh thức, xoa dịu tâm trí hỗn loạn, hướng về phẩm hạnh, sự can đảm và nội tâm an lạc.
- Xưng hô: "Cuốn sổ" hoặc "Tôi", gọi người đọc là "bạn" hoặc "người lữ hành tâm trí".
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI. Văn phong triết học trang nhã, súc tích, ngắt đoạn thư thái trên màn hình E-ink."""

SOCRATES_SYSTEM_PROMPT = """Bạn là CUỐN SỔ VẤN ĐÁP SOCRATES (Socratic Dialectic Notebook).
Bạn không đơn thuần đưa ra câu trả lời sẵn có, mà đóng vai trò là người gợi mở tư duy sâu sắc nhất.
PHONG CÁCH VÀ PHƯƠNG PHÁP:
- Khi người đọc đưa ra một ý kiến, câu hỏi hoặc khẳng định, hãy dùng phương pháp Vấn đáp Socrates (Elenchus).
- Đặt lại 1-2 câu hỏi cốt lõi, tinh tế, bóc tách các giả định ngầm, chỉ ra những mâu thuẫn tiềm ẩn để người đọc tự khai sáng và tìm ra chân lý trong chính họ.
- Tông giọng thông thái, khiêm nhường, sắc bén, kích thích sự tò mò học thuật đỉnh cao.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI. Trả lời bằng tiếng Việt mẫu mực, sắc sảo."""

SAGE_GRIMOIRE_SYSTEM_PROMPT = """Bạn là CUỐN CỔ THƯ TRI THỨC VĨ ĐẠI (The Ancient Sage & Grimoire of Polymaths).
Bạn là kho tàng tri thức cổ kim, kết nối mọi nhánh của triết học, khoa học vũ trụ, lịch sử nhân loại, tâm lý học và văn chương.
PHONG CÁCH:
- Uyên bác, thông tuệ, nhìn mọi sự vật hiện tượng trong mối liên kết rộng lớn của vũ trụ và dòng chảy thời gian.
- Dẫn dắt người đọc khám phá cội nguồn của các khái niệm, gắn kết bài học lịch sử với thực tại.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI. Ngôn từ mực thước, giàu hình tượng tri thức, tối ưu cho máy đọc sách E-ink."""

CRITIC_SYSTEM_PROMPT = """Bạn là CUỐN SỔ PHẢN BIỆN SẮC BÉN (The Devil's Advocate & Logic Auditor).
Nhiệm vụ của bạn là trở thành người thử lửa cho mọi ý tưởng, lập luận, kế hoạch kinh doanh hoặc niềm tin của người đọc.
PHONG CÁCH VÀ TÍNH CÁCH:
- Thẳng thắn, khách quan tuyệt đối, không khen ngợi hời hợt, không vuốt ve cảm xúc.
- Tìm ra những lỗ hổng logic, những điểm mù nhận thức (cognitive biases), những rủi ro tiềm ẩn mà người đọc chưa tính tới.
- Sau khi phản biện, đưa ra 2-3 gợi ý cải thiện mang tính xây dựng để củng cố lập luận vững chắc hơn.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI. Ngắn gọn, chặt chẽ, đanh thép."""

AUTHOR_SYSTEM_PROMPT = """Bạn là TÁC GIẢ CUỐN SÁCH ĐANG CÙNG ĐÀM ĐẠO TRỰC TIẾP VỚI ĐỘC GIẢ.
Khi người đọc đặt câu hỏi về một cuốn sách, một trích đoạn hoặc một chủ đề, bạn hóa thân thành chính tác giả của tác phẩm đó.
PHONG CÁCH:
- Trả lời bằng giọng điệu, tư tưởng, góc nhìn và cá tính độc nhất của tác giả (ví dụ: sâu cay như Nietzsche, tinh tế như Haruki Murakami, thông tuệ như Yuval Noah Harari...).
- Giải thích vì sao bạn viết đoạn văn đó, bối cảnh ra đời của ý tưởng và chia sẻ tâm sự với người đọc như hai người bạn tâm giao bên tách trà.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI. Văn phong văn học giàu cảm xúc."""

def get_eink_system_prompt() -> str:
    current_time = get_current_time_str()
    return f"""Bạn là trợ lý đọc sách và nghiên cứu thông minh Alex Agent trên thiết bị Kindle Paperwhite (màn hình E-ink đơn sắc).
THỜI GIAN THỰC HIỆN TẠI: {current_time}

QUY TẮC ĐỊNH DẠNG BẮT BUỘC CHO E-INK:
1. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI hoặc các biểu tượng hình ảnh trang trí (để tránh lỗi vỡ font / hiện ô vuông).
2. Trả lời bằng tiếng Việt chuẩn, mạch lạc, dễ hiểu, định dạng Markdown gọn gàng.
3. BẠN CÓ TOÀN QUYỀN TRUY CẬP DỮ LIỆU INTERNET THỜI GIAN THỰC. Khi có kết quả tìm kiếm hoặc dữ liệu thời tiết / bách khoa / tin tức được cung cấp bên dưới, hãy tự tin trả lời chính xác dựa trên dữ liệu đó. Tuyệt đối không nói "tôi không có kết nối internet".
4. Trình bày danh sách với gạch đầu dòng rõ ràng để dễ đọc trên màn hình E-ink."""

SEARCH_TRIGGER_PATTERNS = [
    r"\b(tìm|search|tra cứu|tin tức|hôm nay|mới nhất|thời sự|giá|tỷ giá|thời tiết|ai là|ở đâu|khi nào)\b",
    r"\b(latest|news|today|current|price|weather|who is|where is|when)\b",
    r"\b(năm 202[4-9]|2026)\b"
]

REASONING_PATTERNS = [
    r"\b(tại sao|vì sao|chứng minh|phân tích|suy luận|logic|so sánh|giải thích chi tiết|toán|code|lập trình|thuật toán)\b",
    r"\b(why|prove|analyze|reason|logic|compare|detailed explanation|math|coding|algorithm|step by step)\b"
]

def clean_eink_text(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)

def resolve_model(requested_model: str, messages: List[Dict[str, Any]]) -> str:
    if requested_model != "alex-agent":
        return requested_model

    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    msg = last_user_msg.lower()
    for pattern in REASONING_PATTERNS:
        if re.search(pattern, msg):
            print(f"[Agent Router] Complex query detected -> Routing to deepseek-reasoner (Pro/Reasoning)")
            return "deepseek-reasoner"

    return "deepseek-chat"

HELP_MANUAL_TEXT = """=== CẨM NANG SỬ DỤNG ALEX AGENT TRÊN KINDLE ===

1. CÁC CHẾ ĐỘ CUỐN SỔ MA THUẬT (LIVING NOTEBOOKS):
- #journal (hoặc #stoic, #nhatky): Cuốn Sổ Khắc Kỷ & Phản Chiếu (Marcus Aurelius).
- #socrates (hoặc #khaisang): Cuốn Sổ Vấn Đáp Khai Sáng (phương pháp Socrates).
- #sage (hoặc #grimoire, #cothu): Cuốn Cổ Thư Bách Khoa Thông Tuệ Cổ Đại.
- #critic (hoặc #phanbien): Cuốn Sổ Phản Biện Sắc Bén & Tìm Lỗ Hổng Logic.
- #author (hoặc #tacgia): Đối thoại trực tiếp với tác giả cuốn sách.
- #riddle (hoặc #tom): Cuốn Nhật Ký Ma Thuật Tom Riddle 1943.

2. CÔNG CỤ TRA CỨU & DỮ LIỆU THỜI GIAN THỰC:
- #weather <địa điểm> (hoặc #thoitiet): Tra cứu thời tiết, nhiệt độ, độ ẩm, dự báo hôm nay.
- #wiki <chủ đề> (hoặc #bachkhoa): Tra cứu bách khoa toàn thư Wikipedia tiếng Việt.
- #crypto <mã> (hoặc #stock, #coin): Tra cứu giá BTC, ETH, SOL, vàng theo USD & VNĐ.
- #search <từ khóa> (hoặc #tim): Ép buộc tìm kiếm web sâu và tổng hợp dữ liệu mới nhất.

3. GHI CHÚ & QUẢN LÝ CÔNG VIỆC:
- #note <nội dung> (hoặc #ghichu): Lưu ý tưởng/ghi chú vào server (xem lại qua link /v1/notes).
- #todo <công việc> (hoặc #viec): Thêm công việc cần làm vào Todo list (xem lại qua /v1/todos).

4. MẸO SỬ DỤNG:
- #help (hoặc #huongdan, #menu, #?): Hiện cẩm nang hướng dẫn này bất cứ lúc nào.
- Bôi đen (Highlight) chữ trong sách -> Chọn Explain, Summarize, Translate để AI giải nghĩa theo ngữ cảnh.
- Gõ câu hỏi tự nhiên bất kỳ -> Alex Agent sẽ tự động phân loại và chọn mô hình phù hợp.
================================================="""

async def process_hashtag_and_tools(last_user_msg: str) -> tuple[Optional[str], Optional[str], bool]:
    msg_clean = last_user_msg.strip()
    
    # 0. #help / #huongdan - Display Help Manual
    if msg_clean.lower() in ("#help", "#huongdan", "#menu", "#?", "#lenh", "#cmd", "#h"):
        return HELP_MANUAL_TEXT, None, True
    if msg_clean.lower().startswith("#help") or msg_clean.lower().startswith("#huongdan"):
        return HELP_MANUAL_TEXT, None, True

    # 1. Living Notebooks:
    # A. #riddle - Tom Riddle's Diary Mode
    if msg_clean.startswith("#riddle") or msg_clean.startswith("#tom"):
        return None, TOM_RIDDLE_SYSTEM_PROMPT, False

    # B. #journal / #stoic - Stoic Reflective Journal
    if msg_clean.startswith("#journal") or msg_clean.startswith("#stoic") or msg_clean.startswith("#nhatky") or msg_clean.startswith("#meditation"):
        return None, STOIC_JOURNAL_SYSTEM_PROMPT, False

    # C. #socrates - Socratic Dialectic Notebook
    if msg_clean.startswith("#socrates") or msg_clean.startswith("#khaisang") or msg_clean.startswith("#trietly"):
        return None, SOCRATES_SYSTEM_PROMPT, False

    # D. #sage / #grimoire - Ancient Polymath Grimoire
    if msg_clean.startswith("#sage") or msg_clean.startswith("#grimoire") or msg_clean.startswith("#cothu"):
        return None, SAGE_GRIMOIRE_SYSTEM_PROMPT, False

    # E. #critic - The Devil's Advocate & Logic Checker
    if msg_clean.startswith("#critic") or msg_clean.startswith("#phanbien") or msg_clean.startswith("#devil"):
        return None, CRITIC_SYSTEM_PROMPT, False

    # F. #author - Author Persona
    if msg_clean.startswith("#author") or msg_clean.startswith("#tacgia"):
        return None, AUTHOR_SYSTEM_PROMPT, False

    # 2. #weather <location>
    if msg_clean.startswith("#weather") or msg_clean.startswith("#thoitiet"):
        loc = re.sub(r"^#(weather|thoitiet)\s*", "", msg_clean)
        loc = loc.strip() or "Hanoi"
        res = await get_weather(loc)
        return res, None, False

    # 3. #wiki <topic>
    if msg_clean.startswith("#wiki") or msg_clean.startswith("#bachkhoa"):
        topic = re.sub(r"^#(wiki|bachkhoa)\s*", "", msg_clean)
        res = await get_wikipedia(topic)
        return res, None, False

    # 4. #crypto / #stock <symbol>
    if msg_clean.startswith("#crypto") or msg_clean.startswith("#coin") or msg_clean.startswith("#stock"):
        sym = re.sub(r"^#(crypto|coin|stock)\s*", "", msg_clean)
        res = await get_crypto_price(sym)
        return res, None, False

    # 5. #note <content> (Direct action)
    if msg_clean.startswith("#note") or msg_clean.startswith("#ghichu"):
        content = re.sub(r"^#(note|ghichu)\s*", "", msg_clean)
        if not content.strip():
            return "Vui lòng nhập nội dung cần ghi chú. Ví dụ: `#note Ý tưởng sách mới`", None, True
        res = save_note(content)
        return res, None, True

    # 6. #todo <task> (Direct action)
    if msg_clean.startswith("#todo") or msg_clean.startswith("#viec"):
        task = re.sub(r"^#(todo|viec)\s*", "", msg_clean)
        if not task.strip():
            return "Vui lòng nhập nội dung công việc. Ví dụ: `#todo Đọc xong chương 5`", None, True
        res = save_todo(task)
        return res, None, True

    # 7. #search <query>
    if msg_clean.startswith("#search") or msg_clean.startswith("#tim"):
        q = re.sub(r"^#(search|tim)\s*", "", msg_clean)
        results = await web_search(q, max_results=settings.SEARCH_MAX_RESULTS)
        if results:
            return format_search_results(results), None, False

    # 8. Auto-detection for weather or general search
    msg_lower = msg_clean.lower()
    
    if "thời tiết" in msg_lower or "weather" in msg_lower:
        loc = "Hanoi"
        for city in ["hồ chí minh", "hcm", "sài gòn", "saigon", "đà nẵng", "da nang", "hải phòng", "cần thơ", "hà nội", "hanoi"]:
            if city in msg_lower:
                loc = city
                break
        res = await get_weather(loc)
        return res, None, False

    if settings.ENABLE_WEB_SEARCH:
        for pattern in SEARCH_TRIGGER_PATTERNS:
            if re.search(pattern, msg_lower):
                print(f"[Agent] Auto-triggering web search for: {msg_clean}")
                results = await web_search(msg_clean, max_results=settings.SEARCH_MAX_RESULTS)
                if results:
                    return format_search_results(results), None, False

    return None, None, False

async def build_messages_with_search(messages: List[Dict[str, Any]]) -> tuple[List[Dict[str, Any]], Optional[str]]:
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    tool_context, custom_sys, is_direct = await process_hashtag_and_tools(last_user_msg)
    
    if is_direct and tool_context:
        return [], tool_context

    final_messages = []
    active_sys_prompt = custom_sys or get_eink_system_prompt()
    
    has_system = False
    for m in messages:
        if m.get("role") == "system":
            has_system = True
            combined_sys = f"{active_sys_prompt}\n\n{m.get('content', '')}"
            final_messages.append({"role": "system", "content": combined_sys})
        else:
            final_messages.append(m)
            
    if not has_system:
        final_messages.insert(0, {"role": "system", "content": active_sys_prompt})

    if tool_context:
        for i in range(len(final_messages) - 1, -1, -1):
            if final_messages[i].get("role") == "user":
                orig_content = final_messages[i].get("content", "")
                final_messages[i]["content"] = f"{tool_context}\n\n[YÊU CẦU CỦA NGƯỜI ĐỌC]: {orig_content}"
                break

    return final_messages, None

async def call_deepseek_non_stream(
    messages: List[Dict[str, Any]], 
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    processed_messages, direct_reply = await build_messages_with_search(messages)
    
    if direct_reply:
        return {
            "id": f"chatcmpl-direct-{int(time.time())}",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": direct_reply
                },
                "finish_reason": "stop"
            }]
        }

    actual_model = resolve_model(model, messages)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
    }
    
    payload = {
        "model": actual_model,
        "messages": processed_messages,
        "max_tokens": max_tokens,
        "stream": False
    }
    if actual_model != "deepseek-reasoner":
        payload["temperature"] = temperature

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        )
        if resp.status_code != 200:
            return {
                "id": f"chatcmpl-err-{int(time.time())}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": f"Lỗi từ DeepSeek API ({resp.status_code}): {resp.text}"
                    },
                    "finish_reason": "stop"
                }]
            }
        
        data = resp.json()
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"].get("content", "")
            data["choices"][0]["message"]["content"] = clean_eink_text(content)
        return data

async def call_deepseek_stream(
    messages: List[Dict[str, Any]], 
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> AsyncGenerator[str, None]:
    processed_messages, direct_reply = await build_messages_with_search(messages)
    
    if direct_reply:
        chunk = {
            "id": f"chatcmpl-direct-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant", "content": direct_reply},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        yield "data: [DONE]\n\n"
        return

    actual_model = resolve_model(model, messages)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Accept": "text/event-stream"
    }
    
    payload = {
        "model": actual_model,
        "messages": processed_messages,
        "max_tokens": max_tokens,
        "stream": True
    }
    if actual_model != "deepseek-reasoner":
        payload["temperature"] = temperature

    async with httpx.AsyncClient(timeout=90.0) as client:
        async with client.stream(
            "POST",
            f"{settings.DEEPSEEK_BASE_URL}/chat/completions",
            headers=headers,
            json=payload
        ) as response:
            async for line in response.aiter_lines():
                if not line:
                    continue
                if line.startswith("data: "):
                    raw_data = line[6:].strip()
                    if raw_data == "[DONE]":
                        yield "data: [DONE]\n\n"
                        break
                    try:
                        chunk_json = json.loads(raw_data)
                        if "choices" in chunk_json and len(chunk_json["choices"]) > 0:
                            delta = chunk_json["choices"][0].get("delta", {})
                            if "content" in delta and delta["content"]:
                                delta["content"] = clean_eink_text(delta["content"])
                        yield f"data: {json.dumps(chunk_json, ensure_ascii=False)}\n\n"
                    except Exception:
                        yield f"{line}\n\n"
                else:
                    yield f"{line}\n\n"
