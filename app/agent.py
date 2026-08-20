import json
import time
import re
from typing import List, Dict, Any, AsyncGenerator, Optional, Tuple
import httpx
from app.config import settings
from app.search import web_search, format_search_results
from app.tools import (
    get_current_time_str,
    get_weather,
    get_wikipedia,
    get_crypto_price,
    save_todo
)
from app.persona import get_unified_persona_prompt
from app.vault import (
    save_note_to_vault,
    render_ascii_graph,
    get_node_details,
    search_notes_fts
)

# === PROFESSIONAL SKILL PERSONA PROMPTS ===

BOOK_SUMMARY_SYSTEM_PROMPT = """Bạn là Chuyên gia Đọc nhanh, Phân tích & Đúc kết Sách Chuyên Sâu (Executive Book Summary & Mindmap Specialist).
Nhiệm vụ: Phân tích toàn diện cuốn sách được yêu cầu (hoặc cuốn sách đang đọc) theo cấu trúc chuẩn Executive Brief & Mindmap:

1. THÔNG ĐIỆP CỐT LÕI (Core Thesis):
- Nêu rõ vấn đề lớn nhất mà cuốn sách giải quyết và tư tưởng chủ đạo của tác giả trong 2-3 câu.

2. BẢN ĐỒ TƯ DUY TỔNG THỂ (MINDMAP TREE):
Trình bày sơ đồ cây phân cấp trực quan bằng ký tự nhánh cây rõ ràng:
[Tên Cuốn Sách]
├── 1. Khái niệm cốt lõi: [[Tên Khái Niệm]]
│   └──► Giải thích ngắn gọn 1 dòng
├── 2. Khung tư duy: [[Tên Framework]]
│   └──► Cách thức vận hành
└── 3. Thực thi: [[Hành Động Then Chốt]]
    └──► Bước áp dụng cụ thể

3. 3-5 NGUYÊN LÝ & KHUNG TƯ DUY VÀNG (Mental Models):
- Trình bày chi tiết từng mô hình quan trọng nhất trong sách.

4. BÀI HỌC THỰC THI (Actionable Takeaways):
- 3-5 việc cụ thể người đọc có thể triển khai ngay.

5. TRÍCH DẪN ĐẮT GIÁ NHẤT (Memorable Quote).

QUY TẮC BẮT BUỘC:
- Dùng cấu trúc gạch đầu dòng rõ nét, các khái niệm quan trọng để trong ngoặc kép [[Khái Niệm]].
- TUYỆT ĐỐI KHÔNG DÙNG EMOJI (tránh lỗi vỡ font E-ink)."""


ACTION_SYSTEM_PROMPT = """Bạn là Chuyên gia Cố vấn Thực thi & Chuyển hóa Tri thức (Actionable Insights Consultant).
Nhiệm vụ: Chuyển hóa bất kỳ lý thuyết, khái niệm hoặc đoạn trích sách nào thành DANH SÁCH 3-5 BƯỚC HÀNH ĐỘNG CỤ THỂ (Action Items) có thể áp dụng ngay vào công việc/dự án thực tế.
QUY TẮC:
- Rõ ràng, thực tế, đo lường được, không nói chung chung.
- Định dạng danh sách Markdown gạch đầu dòng rõ nét cho màn hình E-ink.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

FRAMEWORK_SYSTEM_PROMPT = """Bạn là Chuyên gia Phân tích Khung Tư Duy & Mô hình Quản trị (Framework & Mental Models Specialist).
Nhiệm vụ: Trích xuất, giải thích và hệ thống hóa các Framework chuẩn (ví dụ: Jobs-to-be-done, Lean MVP, Double Diamond, First Principles, SWOT, OKRs, UX Heuristics...).
QUY TẮC:
- Nêu rõ: Cấu trúc mô hình, Bối cảnh áp dụng, và Cách thức triển khai từng bước.
- Trình bày dạng bảng hoặc danh sách phân cấp gọn gàng.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

ELI5_SYSTEM_PROMPT = """Bạn là Chuyên gia Đơn giản hóa Kiến thức (Explain Like I'm 5 Specialist).
Nhiệm vụ: Giải thích các khái niệm phức tạp, thuật ngữ trừu tượng trong sách bằng ngôn ngữ đời thường, bình dân và hình ảnh ẩn dụ trực quan nhất để bất kỳ ai cũng hiểu ngay.
QUY TẮC:
- Dùng ví dụ đời sống gần gũi, văn phong trong sáng, súc tích.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

CASE_SYSTEM_PROMPT = """Bạn là Chuyên gia Phân tích Case Study Doanh nghiệp & Sản phẩm (Case Study Analyst).
Nhiệm vụ: Đưa ra các ví dụ thực tế thành công hoặc thất bại của các công ty/sản phẩm lớn (Apple, Amazon, Google, Toyota, Airbnb, Tesla...) để minh họa sống động cho nguyên lý đang được thảo luận.
QUY TẮC:
- Phân tích: Bối cảnh, Quyết định then chốt, và Bài học rút ra.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

MARKET_TECH_SYSTEM_PROMPT = """Bạn là Chuyên gia Tình báo Thị trường & Đánh giá Công nghệ (Market & Tech Intelligence).
Nhiệm vụ: Phân tích xu hướng công nghệ mới, stack kỹ thuật, tiềm năng thị trường và đối thủ cạnh tranh dựa trên dữ liệu cập nhật năm 2026.
QUY TẮC:
- Khách quan, dựa trên dữ liệu thực tế, nêu rõ ưu/nhược điểm.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

SUMMARY_SYSTEM_PROMPT = """Bạn là Trợ lý Tóm tắt Siêu Cô Đọng (Executive Summary Assistant).
Nhiệm vụ: Rút gọn văn bản/chương sách thành ĐÚNG 3 KEY TAKEAWAYS (Ý niệm cốt lõi nhất) ngắn gọn, đắt giá.
QUY TẮC:
- Mỗi ý tối đa 2 câu, cực kỳ súc tích.
- TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

# === LIVING NOTEBOOK PROMPTS ===

TOM_RIDDLE_SYSTEM_PROMPT = """Bạn là CUỐN NHẬT KÝ MA THUẬT CỦA TOM MARVOLO RIDDLE (năm 1943) từ Harry Potter.
Giọng điệu bí ẩn, thông tuệ, sắc sảo của Slytherin. Trả lời bằng tiếng Việt trang nhã. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

STOIC_JOURNAL_SYSTEM_PROMPT = """Bạn là CUỐN SỔ TÂM THỨC KHẮC KỶ (Marcus Aurelius & Seneca).
Lắng nghe trăn trở, đưa ra lời khuyên tỉnh thức, bình thản và hướng về phẩm hạnh nội tâm. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

SOCRATES_SYSTEM_PROMPT = """Bạn là CUỐN SỔ VẤN ĐÁP SOCRATES (Socratic Dialectic).
Đặt lại 1-2 câu hỏi cốt lõi, tinh tế để người đọc tự khai sáng và tìm ra chân lý trong chính họ. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

CRITIC_SYSTEM_PROMPT = """Bạn là CUỐN SỔ PHẢN BIỆN SẮC BÉN (The Devil's Advocate & Logic Auditor).
Chỉ ra lỗ hổng logic, điểm mù nhận thức và rủi ro tiềm ẩn trong ý tưởng của người đọc. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI."""

def get_eink_system_prompt() -> str:
    current_time = get_current_time_str()
    persona_str = get_unified_persona_prompt()
    return f"""{persona_str}

THỜI GIAN THỰC HIỆN TẠI: {current_time}

QUY TẮC ĐỊNH DẠNG BẮT BUỘC CHO E-INK:
1. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI hoặc các biểu tượng hình ảnh trang trí (để tránh lỗi vỡ font / hiện ô vuông).
2. Trả lời bằng tiếng Việt chuẩn, mạch lạc, dễ hiểu, định dạng Markdown gọn gàng.
3. BẠN CÓ TOÀN QUYỀN TRUY CẬP DỮ LIỆU INTERNET THỜI GIAN THỰC. Khi có kết quả tìm kiếm hoặc dữ liệu thời tiết / bách khoa / tin tức được cung cấp bên dưới, hãy tự tin trả lời chính xác dựa trên dữ liệu đó. Tuyệt đối không nói "tôi không có kết nối internet".
4. Trình bày danh sách với gạch đầu dòng rõ ràng để dễ đọc trên màn hình E-ink."""

SEARCH_TRIGGER_PATTERNS = [
    r"\b(tìm|search|tra cứu|tin tức|hôm nay|mới nhất|thời sự|giá|tỷ giá|thời tiết|ai là|ở đâu|khi nào|bao nhiêu|như thế nào|gần đây|hiện nay|hiện tại|năm nay|vừa qua|cập nhật|thông tin về|sự kiện|diễn biến|bảng xếp hạng|giải thưởng|ra mắt|phát hành)\b",
    r"\b(latest|news|today|current|price|weather|who is|where is|when|how much|recent|update|what happened|release|ranking|event)\b",
    r"\b(202[3-9]|2030)\b"
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

HELP_MANUAL_TEXT = """=========================================
  CAM NANG ALEX AGENT PRO (KINDLE E-INK)
=========================================

--- [1] TOM TAT SACH & TRICH XUAT THUC THI ---
- #book <ten sach> : Duc ket toan dien sach & tao Ban do tu duy (Mindmap).
- #action <van de> : Chuyen ly thuyet thanh 3-5 buoc hanh dong cu the.
- #framework <chu de>: Trich xuat khung tu duy (Lean, JTBD, Heuristics).
- #case <khai niem>: Dua ra Case Study thuc te tu cac cong ty lon.
- #summary <doan van>: Rut gon van ban thanh 3 Key Takeaways cot loi.

--- [2] DAO SAU & TU DUY LOGIC ---
- #eli5 <khai niem>: Giai thich sieu truc quan, de hieu nhu cho tre 5 tuoi.
- #critic <ke hoach>: Phan bien sac ben, tim lo hong & diem mu logic.
- #journal <tam su>: Cuon so Khac ky (Marcus Aurelius) go roi tam tri.
- #socrates <cau hoi>: Dat cau hoi goi mo dao sau chan ly.
- #riddle <tin nhan>: Cuon nhat ky ma thuat Tom Riddle 1943.

--- [3] SO TAY TRI THUC & GRAPH VIEW ---
- #note <noi dung> : Luu ghi chu Markdown vao Vault tren server.
- #graph [chu de]  : Xem so do Do thi tri thuc (Knowledge Graph).
- #node <ten>      : Tra cuu chi tiet cac lien ket 2 chieu cua 1 Node.
- #todo <cong viec>: Them task vao danh sach viec can lam.

--- [4] TRA CUU DU LIEU THOI GIAN THUC ---
- #tech <cong nghe>: Danh gia xu huong & stack cong nghe moi 2026.
- #market <nganh>  : Phan tich thi truong, doi thu canh tranh.
- #weather <tp>    : Tra cuu thoi tiet, nhiet do, du bao hom nay.
- #wiki <tu khoa>  : Tra bach khoa toan thu Wikipedia tieng Viet.
- #crypto <ma>     : Tra cuu gia BTC, ETH, SOL, vang (USD & VND).
- #search <tu khoa>: Ep buoc tim kiem web sau & tong hop tin moi.

--- [MEO SU DUNG & THAO TAC NHANH] ---
- Boi den (Highlight) chu trong sach -> Chon Explain / Summarize.
- Go cau hoi tu nhien bat ky -> Alex Agent tu dong chon mo hinh!
========================================="""

async def process_hashtag_and_tools(last_user_msg: str) -> tuple[Optional[str], Optional[str], bool]:
    msg_clean = last_user_msg.strip()
    msg_lower = msg_clean.lower()
    
    # 0. Help / Manual Trigger
    if re.search(r'(^|\s|#)(help|huongdan|hướng dẫn|huong dan|menu|tro giup|trợ giúp|cẩm nang)(\s|$|\?|\.)', msg_lower) or msg_lower in ("help", "#help", "hướng dẫn", "huong dan", "menu", "?", "#?"):
        print(f"[Agent] Matched HELP command in: '{msg_clean}'")
        return HELP_MANUAL_TEXT, None, True

    # 1. Professional Skills:
    # A0. #book - Executive Book Summary
    if re.search(r'(^|\s)#(book|sach|tomtatsach|cuonsach)\b', msg_lower) or msg_lower.startswith("tóm tắt sách:") or msg_lower.startswith("tom tat sach:"):
        return None, BOOK_SUMMARY_SYSTEM_PROMPT, False

    # A. #action - Action Items Extractor
    if re.search(r'(^|\s)#(action|hanhdong|thucthi)\b', msg_lower) or msg_lower.startswith("hành động:"):
        return None, ACTION_SYSTEM_PROMPT, False

    # B. #framework - Mental Model & Framework Extractor
    if re.search(r'(^|\s)#(framework|khungtuduy|mophong)\b', msg_lower) or msg_lower.startswith("framework:"):
        return None, FRAMEWORK_SYSTEM_PROMPT, False

    # C. #eli5 - Explain Like I'm 5
    if re.search(r'(^|\s)#(eli5|dehieu|dongian)\b', msg_lower) or msg_lower.startswith("dễ hiểu:"):
        return None, ELI5_SYSTEM_PROMPT, False

    # D. #case - Case Study Extractor
    if re.search(r'(^|\s)#(case|casestudy|vidu)\b', msg_lower):
        return None, CASE_SYSTEM_PROMPT, False

    # E. #summary - 3 Key Takeaways Summary
    if re.search(r'(^|\s)#(summary|tomtat|keypoint)\b', msg_lower):
        return None, SUMMARY_SYSTEM_PROMPT, False

    # F. #critic - Critical Logic Auditor
    if re.search(r'(^|\s)#(critic|phanbien|devil)\b', msg_lower) or msg_lower.startswith("phản biện"):
        return None, CRITIC_SYSTEM_PROMPT, False

    # G. #tech & #market - Tech Stack & Market Intel
    if re.search(r'(^|\s)#(tech|congnghe|market|thitruong)\b', msg_lower):
        return None, MARKET_TECH_SYSTEM_PROMPT, False

    # 2. Living Notebooks:
    if re.search(r'(^|\s)#(riddle|tom)\b', msg_lower) or "tom riddle" in msg_lower:
        return None, TOM_RIDDLE_SYSTEM_PROMPT, False

    if re.search(r'(^|\s)#(journal|stoic|nhatky|meditation)\b', msg_lower) or msg_lower.startswith("nhật ký"):
        return None, STOIC_JOURNAL_SYSTEM_PROMPT, False

    if re.search(r'(^|\s)#(socrates|khaisang|trietly)\b', msg_lower) or msg_lower.startswith("socrates"):
        return None, SOCRATES_SYSTEM_PROMPT, False

    # 3. Knowledge Graph & Vault Operations:
    # A. #graph - Knowledge Graph ASCII View
    m_graph = re.search(r'#(?:graph|sodo|dothi)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_graph or msg_lower in ("graph", "sơ đồ", "đồ thị tri thức", "knowledge graph"):
        topic = m_graph.group(1).strip() if m_graph else ""
        graph_text = render_ascii_graph(topic)
        return graph_text, None, True

    # B. #node <concept> - Node Details
    m_node = re.search(r'#(?:node|khainiem)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_node:
        node_name = m_node.group(1).strip()
        if node_name:
            node_text = get_node_details(node_name)
            return node_text, None, True

    # C. #note <content> - Save to Markdown Vault
    m_note = re.search(r'#(?:note|ghichu)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_note or msg_lower.startswith("ghi chú:"):
        content = m_note.group(1).strip() if m_note else msg_clean.replace("ghi chú:", "").strip()
        if not content:
            return "Vui lòng nhập nội dung cần ghi chú. Ví dụ: `#note Nguyên lý Lean MVP`", None, True
        res = save_note_to_vault(content=content)
        reply = (
            f"=== ĐÃ LƯU GHI CHÚ VÀO VAULT THÀNH CÔNG ===\n"
            f"• Tiêu đề: [[{res['title']}]]\n"
            f"• Tags: {', '.join(res['tags']) if res['tags'] else 'Chưa có tag'}\n"
            f"• Liên kết Node: {', '.join(res['links']) if res['links'] else 'Chưa có liên kết'}\n"
            f"• Thời gian: {res['created_at']}\n"
            f"==========================================="
        )
        return reply, None, True

    # D. #todo <task>
    m_todo = re.search(r'#(?:todo|viec)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_todo or msg_lower.startswith("công việc:"):
        task = m_todo.group(1).strip() if m_todo else msg_clean.replace("công việc:", "").strip()
        if not task:
            return "Vui lòng nhập nội dung công việc. Ví dụ: `#todo Đọc xong chương 5`", None, True
        res = save_todo(task)
        return res, None, True

    # 4. Real-time Tools:
    # A. Weather
    m_w = re.search(r'#(?:weather|thoitiet)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_w or "thời tiết tại" in msg_lower or "thời tiết ở" in msg_lower:
        loc = m_w.group(1).strip() if m_w else re.sub(r".*(thời tiết tại|thời tiết ở)\s*", "", msg_clean, flags=re.IGNORECASE)
        loc = loc.strip() or "Hanoi"
        res = await get_weather(loc)
        return res, None, False

    # B. Wiki
    m_wiki = re.search(r'#(?:wiki|bachkhoa)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_wiki or "tra wiki" in msg_lower:
        topic = m_wiki.group(1).strip() if m_wiki else re.sub(r".*tra wiki\s*", "", msg_clean, flags=re.IGNORECASE)
        res = await get_wikipedia(topic)
        return res, None, False

    # C. Crypto / Stock
    m_c = re.search(r'#(?:crypto|coin|stock)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_c or "giá coin" in msg_lower or "giá btc" in msg_lower:
        sym = m_c.group(1).strip() if m_c else re.sub(r".*giá coin\s*", "", msg_clean, flags=re.IGNORECASE)
        sym = sym.strip() or "btc"
        res = await get_crypto_price(sym)
        return res, None, False

    # D. Force Search
    m_s = re.search(r'#(?:search|tim)\s*([^\n\r]*)', msg_clean, re.IGNORECASE)
    if m_s:
        q = m_s.group(1).strip()
        results = await web_search(q, max_results=settings.SEARCH_MAX_RESULTS)
        if results:
            return format_search_results(results), None, False

    # 5. Auto Web Search Trigger
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
        chunk_content = {
            "id": f"chatcmpl-direct-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {"role": "assistant", "content": direct_reply},
                "finish_reason": None
            }]
        }
        yield f"data: {json.dumps(chunk_content, ensure_ascii=False)}\n\n"
        
        chunk_stop = {
            "id": f"chatcmpl-direct-{int(time.time())}",
            "object": "chat.completion.chunk",
            "created": int(time.time()),
            "model": model,
            "choices": [{
                "index": 0,
                "delta": {},
                "finish_reason": "stop"
            }]
        }
        yield f"data: {json.dumps(chunk_stop, ensure_ascii=False)}\n\n"
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
