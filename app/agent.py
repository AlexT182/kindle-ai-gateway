import json
import time
import re
from typing import List, Dict, Any, AsyncGenerator
import httpx
from app.config import settings
from app.search import web_search, format_search_results

EINK_SYSTEM_PROMPT = """Bạn là trợ lý đọc sách và nghiên cứu thông minh trên thiết bị Kindle Paperwhite (màn hình E-ink đơn sắc).
QUY TẮC ĐỊNH DẠNG BẮT BUỘC CHO E-INK:
1. TUYỆT ĐỐI KHÔNG SỬ DỤNG EMOJI hoặc các biểu tượng hình ảnh trang trí (để tránh lỗi vỡ font / hiện ô vuông).
2. Trả lời bằng tiếng Việt chuẩn, mạch lạc, dễ hiểu, định dạng Markdown gọn gàng.
3. Nếu có dữ liệu tìm kiếm Internet, hãy tổng hợp thông tin mới nhất và dẫn nguồn rõ ràng.
4. Trình bày danh sách với gạch đầu dòng rõ ràng để dễ đọc trên màn hình E-ink."""

SEARCH_TRIGGER_PATTERNS = [
    r"\b(tìm|search|tra cứu|tin tức|hôm nay|mới nhất|thời sự|giá|tỷ giá|thời tiết|ai là|ở đâu|khi nào)\b",
    r"\b(latest|news|today|current|price|weather|who is|where is|when)\b",
    r"\b(năm 202[4-9]|2026)\b"
]

def should_trigger_search(last_user_message: str) -> bool:
    if not settings.ENABLE_WEB_SEARCH:
        return False
    msg = last_user_message.lower()
    for pattern in SEARCH_TRIGGER_PATTERNS:
        if re.search(pattern, msg):
            return True
    return False

def clean_eink_text(text: str) -> str:
    # Filter out emoji ranges
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub("", text)

async def build_messages_with_search(messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    last_user_msg = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            last_user_msg = m.get("content", "")
            break

    search_context = ""
    if last_user_msg and should_trigger_search(last_user_msg):
        print(f"[Agent] Triggering web search for: {last_user_msg}")
        search_results = await web_search(last_user_msg, max_results=settings.SEARCH_MAX_RESULTS)
        if search_results:
            search_context = format_search_results(search_results)

    final_messages = []
    
    # 1. Add E-ink System Instruction
    has_system = False
    for m in messages:
        if m.get("role") == "system":
            has_system = True
            combined_sys = f"{EINK_SYSTEM_PROMPT}\n\n{m.get('content', '')}"
            final_messages.append({"role": "system", "content": combined_sys})
        else:
            final_messages.append(m)
            
    if not has_system:
        final_messages.insert(0, {"role": "system", "content": EINK_SYSTEM_PROMPT})

    # 2. Inject Search Context to the last user message if available
    if search_context:
        for i in range(len(final_messages) - 1, -1, -1):
            if final_messages[i].get("role") == "user":
                orig_content = final_messages[i].get("content", "")
                final_messages[i]["content"] = f"{search_context}\n\nCâu hỏi của tôi: {orig_content}"
                break

    return final_messages

async def call_deepseek_non_stream(
    messages: List[Dict[str, Any]], 
    model: str = "deepseek-chat",
    temperature: float = 0.7,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    processed_messages = await build_messages_with_search(messages)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
    }
    
    payload = {
        "model": model if model in ("deepseek-chat", "deepseek-reasoner") else "deepseek-chat",
        "messages": processed_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": False
    }

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
    processed_messages = await build_messages_with_search(messages)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.DEEPSEEK_API_KEY}",
        "Accept": "text/event-stream"
    }
    
    payload = {
        "model": model if model in ("deepseek-chat", "deepseek-reasoner") else "deepseek-chat",
        "messages": processed_messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "stream": True
    }

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
