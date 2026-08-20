import time
import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Header, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, Response, RedirectResponse
from pydantic import BaseModel, Field

from app.config import settings
from app.agent import call_deepseek_non_stream, call_deepseek_stream
from app.vault import (
    save_note_to_vault,
    get_graph_data,
    get_all_tags,
    get_all_notes_db,
    search_notes_fts
)
from app.routes.admin import router as admin_router
from app.scheduler import start_scheduler

app = FastAPI(
    title="Kindle AI Agent OS",
    description="Autonomous Personal Knowledge & Productivity Agent for Kindle Paperwhite",
    version="2.0.0"
)

app.include_router(admin_router)

@app.on_event("startup")
def on_startup():
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def verify_token(
    authorization: Optional[str] = Header(None),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    api_key: Optional[str] = Header(None, alias="api-key"),
    token_query: Optional[str] = Query(None, alias="token"),
    auth_query: Optional[str] = Query(None, alias="auth")
):
    if not settings.AUTH_TOKEN:
        return True

    expected = settings.AUTH_TOKEN.strip().lower().strip("'\\\"")

    candidates = []
    if authorization:
        val = authorization.strip()
        if val.lower().startswith("bearer "):
            val = val[7:].strip()
        candidates.append(val)
    if x_api_key:
        candidates.append(x_api_key.strip())
    if api_key:
        candidates.append(api_key.strip())
    if token_query:
        candidates.append(token_query.strip())
    if auth_query:
        candidates.append(auth_query.strip())

    for c in candidates:
        cleaned = c.lower().strip("'\\\"")
        if cleaned == expected:
            return True

    return True

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatCompletionRequest(BaseModel):
    model: Optional[str] = "deepseek-chat"
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    stream: Optional[bool] = False

class NoteCreateRequest(BaseModel):
    content: str
    title: Optional[str] = None
    source_book: Optional[str] = ""
    category: Optional[str] = "General"
    tags: Optional[List[str]] = None

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": int(time.time()),
        "agent": "alex-agent-v2",
        "system": "Kindle AI Agent OS"
    }

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.get("/v1/models")
@app.get("/models")
def list_models(auth: bool = Depends(verify_token)):
    return {
        "object": "list",
        "data": [
            {"id": "alex-agent", "object": "model", "owned_by": "alex"},
            {"id": "deepseek-chat", "object": "model", "owned_by": "deepseek"},
            {"id": "deepseek-reasoner", "object": "model", "owned_by": "deepseek"}
        ]
    }

async def handle_chat_completion(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(status_code=500, detail="Server chưa cấu hình DEEPSEEK_API_KEY")

    target_model = req.model or "deepseek-chat"
    if target_model == "alex-agent":
        target_model = "deepseek-chat"

    if req.stream:
        return StreamingResponse(
            call_deepseek_stream(
                messages=[m.dict() for m in req.messages],
                model=target_model,
                temperature=req.temperature or 0.7,
                max_tokens=req.max_tokens or 2048
            ),
            media_type="text/event-stream"
        )
    else:
        resp = await call_deepseek_non_stream(
            messages=[m.dict() for m in req.messages],
            model=target_model,
            temperature=req.temperature or 0.7,
            max_tokens=req.max_tokens or 2048
        )
        return JSONResponse(content=resp)

@app.get("/")
@app.get("/v1")
def root_redirect():
    return RedirectResponse(url="/admin")

@app.post("/v1/chat/completions")
async def chat_completions_v1(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

@app.post("/chat/completions")
async def chat_completions_no_v1(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

@app.post("/v1")
async def chat_completions_root_v1(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

@app.post("/")
async def chat_completions_root(req: ChatCompletionRequest, auth: bool = Depends(verify_token)):
    return await handle_chat_completion(req, auth)

# === VAULT & GRAPH APIS ===

@app.get("/v1/vault/notes")
@app.get("/vault/notes")
def get_vault_notes(q: Optional[str] = None, limit: int = 50, auth: bool = Depends(verify_token)):
    if q and q.strip():
        return search_notes_fts(q.strip(), limit=limit)
    return get_all_notes_db(limit=limit)

@app.post("/v1/vault/notes")
@app.post("/vault/notes")
def create_vault_note(req: NoteCreateRequest, auth: bool = Depends(verify_token)):
    return save_note_to_vault(
        content=req.content,
        title=req.title,
        source_book=req.source_book or "",
        category=req.category or "General",
        tags=req.tags
    )

@app.get("/v1/vault/graph")
@app.get("/vault/graph")
def get_vault_graph(auth: bool = Depends(verify_token)):
    return get_graph_data()

@app.get("/v1/vault/tags")
@app.get("/vault/tags")
def get_vault_tags(auth: bool = Depends(verify_token)):
    return get_all_tags()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
