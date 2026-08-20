import os
import json
from typing import Dict, Any, List

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
CONFIG_DIR = os.path.join(DATA_DIR, "config")
os.makedirs(CONFIG_DIR, exist_ok=True)
MCP_REGISTRY_FILE = os.path.join(CONFIG_DIR, "mcp_registry.json")

DEFAULT_MCP_REGISTRY = {
    "servers": [
        {
            "id": "web_search_mcp",
            "name": "Web Search Engine",
            "description": "Tìm kiếm web thời gian thực qua DuckDuckGo và Tavily.",
            "enabled": True,
            "type": "native",
            "tools": ["web_search", "news_search"]
        },
        {
            "id": "vault_filesystem_mcp",
            "name": "Vault Knowledge Graph & Markdown",
            "description": "Đọc, ghi, liên kết file Markdown và tra cứu đồ thị tri thức.",
            "enabled": True,
            "type": "native",
            "tools": ["save_note", "search_vault", "get_graph"]
        },
        {
            "id": "weather_mcp",
            "name": "Live Weather Service",
            "description": "Tra cứu nhiệt độ, độ ẩm và dự báo thời tiết qua wttr.in.",
            "enabled": True,
            "type": "native",
            "tools": ["get_weather"]
        },
        {
            "id": "finance_mcp",
            "name": "Live Financial & Crypto Intel",
            "description": "Lấy giá Bitcoin, ETH, SOL, vàng và cổ phiếu theo USD/VNĐ.",
            "enabled": True,
            "type": "native",
            "tools": ["get_crypto_price"]
        }
    ]
}

def get_mcp_registry() -> Dict[str, Any]:
    if os.path.exists(MCP_REGISTRY_FILE):
        try:
            with open(MCP_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_MCP_REGISTRY

def save_mcp_registry(registry: Dict[str, Any]):
    with open(MCP_REGISTRY_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, ensure_ascii=False, indent=2)

def toggle_mcp_server(server_id: str, enabled: bool) -> bool:
    reg = get_mcp_registry()
    for s in reg.get("servers", []):
        if s["id"] == server_id:
            s["enabled"] = enabled
            save_mcp_registry(reg)
            return True
    return False

def add_mcp_server(server_id: str, name: str, description: str, endpoint: str = "", command: str = ""):
    reg = get_mcp_registry()
    reg.setdefault("servers", []).append({
        "id": server_id,
        "name": name,
        "description": description,
        "endpoint": endpoint,
        "command": command,
        "enabled": True,
        "type": "custom",
        "tools": []
    })
    save_mcp_registry(reg)
