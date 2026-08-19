import asyncio
import httpx
from typing import List, Dict
from app.config import settings

async def search_tavily(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    if not settings.TAVILY_API_KEY:
        return []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": settings.TAVILY_API_KEY,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": max_results,
                },
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for item in data.get("results", []):
                    results.append({
                        "title": item.get("title", ""),
                        "url": item.get("url", ""),
                        "content": item.get("content", ""),
                    })
                return results
    except Exception as e:
        print(f"[Search Tavily Error]: {e}")
    return []

def search_duckduckgo_sync(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    try:
        from duckduckgo_search import DDGS
        with DDGS() as ddgs:
            raw_results = list(ddgs.text(query, max_results=max_results))
            results = []
            for item in raw_results:
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("href", ""),
                    "content": item.get("body", ""),
                })
            return results
    except Exception as e:
        print(f"[Search DDG Error]: {e}")
        return []

async def web_search(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    # Priority 1: Tavily (if configured)
    if settings.TAVILY_API_KEY:
        results = await search_tavily(query, max_results=max_results)
        if results:
            return results
    
    # Priority 2: DuckDuckGo (Free / No key required)
    loop = asyncio.get_event_loop()
    results = await loop.run_in_executor(None, search_duckduckgo_sync, query, max_results)
    return results

def format_search_results(results: List[Dict[str, str]]) -> str:
    if not results:
        return ""
    formatted = ["=== KẾT QUẢ TÌM KIẾM INTERNET THỜI GIAN THỰC ==="]
    for i, r in enumerate(results, 1):
        formatted.append(f"[{i}] {r['title']}
Nguồn: {r['url']}
Nội dung: {r['content']}
")
    formatted.append("================================================")
    return "\n".join(formatted)
