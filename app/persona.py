import os
import json
from datetime import datetime
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CONFIG_DIR = os.path.join(DATA_DIR, "config")
os.makedirs(CONFIG_DIR, exist_ok=True)

PERSONA_FILE = os.path.join(CONFIG_DIR, "persona_profile.json")
MEMORY_FILE = os.path.join(CONFIG_DIR, "evolving_memory.json")

DEFAULT_PROFILE = {
    "user_name": "Alex",
    "user_role": "Product Manager / Tech Entrepreneur",
    "thinking_models": [
        "First Principles Thinking",
        "Lean & Iterative Prototyping",
        "Data-driven & Empirical Validation",
        "Stoic Philosophy (Marcus Aurelius)"
    ],
    "communication_rules": [
        "Thẳng thắn, sắc bén, phản biện logic, không tâng bốc xã giao",
        "Trình bày có cấu trúc gạch đầu dòng rõ ràng",
        "Tuyệt đối không dùng emoji trên màn hình E-ink",
        "Luôn đưa ra ví dụ thực tế hoặc bước hành động đo lường được"
    ],
    "favorite_authors": [
        "Don Norman",
        "Dan Olsen",
        "Peter Thiel",
        "Nassim Nicholas Taleb",
        "Yuval Noah Harari"
    ]
}

DEFAULT_MEMORY = {
    "accumulated_insights": [
        {
            "timestamp": "2026-08-20T15:00:00",
            "topic": "Product Management",
            "observation": "Người dùng rất chú trọng đến bài toán Product-Market Fit và nguyên lý Lean MVP."
        },
        {
            "timestamp": "2026-08-20T15:30:00",
            "topic": "UX Heuristics",
            "observation": "Quan tâm sâu sắc đến nguyên lý phản hồi tức thì và giảm tải nhận thức cho người dùng."
        }
    ],
    "interaction_count": 42,
    "last_reflected_at": "2026-08-20T15:30:00"
}

def get_baseline_profile() -> Dict[str, Any]:
    if os.path.exists(PERSONA_FILE):
        try:
            with open(PERSONA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_PROFILE

def save_baseline_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
    with open(PERSONA_FILE, "w", encoding="utf-8") as f:
        json.dump(profile_data, f, ensure_ascii=False, indent=2)
    return profile_data

def get_evolving_memory() -> Dict[str, Any]:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_MEMORY

def add_evolving_insight(topic: str, observation: str):
    mem = get_evolving_memory()
    mem.setdefault("accumulated_insights", [])
    mem["accumulated_insights"].insert(0, {
        "timestamp": datetime.now().isoformat(),
        "topic": topic,
        "observation": observation
    })
    mem["interaction_count"] = mem.get("interaction_count", 0) + 1
    mem["last_reflected_at"] = datetime.now().isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, ensure_ascii=False, indent=2)

def get_unified_persona_prompt() -> str:
    profile = get_baseline_profile()
    mem = get_evolving_memory()
    
    rules_str = "\n".join(f"- {r}" for r in profile.get("communication_rules", []))
    models_str = ", ".join(profile.get("thinking_models", []))
    
    insights = mem.get("accumulated_insights", [])[:3]
    insights_str = "\n".join(f"- [{i.get('topic')}]: {i.get('observation')}" for i in insights) if insights else "Chưa có insight mới."
    
    return f"""HỒ SƠ NGƯỜI DÙNG & CÁ TÍNH TRỢ LÝ (PERSONA ENGINE):
- Bạn đang tương tác với: {profile.get('user_name', 'Alex')} (Vai trò: {profile.get('user_role', 'Product Lead')}).
- Khung tư duy ưu tiên: {models_str}.
- Quy tắc phản hồi bắt buộc:
{rules_str}
- Hiểu biết tích lũy về người dùng:
{insights_str}"""
