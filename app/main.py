import time
import uuid
import logging
from contextlib import asynccontextmanager
from typing import List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response, StreamingResponse
from pydantic import BaseModel, Field

from app.agent import call_deepseek_non_stream, call_deepseek_stream
from app.agent_runtime import run_agent_completion, run_agent_stream
from app.auth import require_api_token
from app.config import APP_VERSION, settings
from app.db import database_is_ready
from app.routes.admin import router as admin_router
from app.scheduler import shutdown_scheduler, start_scheduler
from app.vault import generate_kindle_graph_image, get_all_notes_db, get_all_tags, get_graph_data, save_note_to_vault, search_notes_fts

request_logger = logging.getLogger("kindle.gateway")
request_logger.setLevel(logging.INFO)


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings.validate_security()
    if settings.ENABLE_SCHEDULER:
        start_scheduler()
    yield
    shutdown_scheduler()


app = FastAPI(title="Kindle AI Agent OS", version=APP_VERSION, lifespan=lifespan,
              docs_url="/docs" if settings.ENABLE_DOCS else None,
              redoc_url="/redoc" if settings.ENABLE_DOCS else None,
              openapi_url="/openapi.json" if settings.ENABLE_DOCS else None)
app.include_router(admin_router)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    request_id = str(uuid.uuid4())
    started = time.perf_counter()
    try:
        response = await call_next(request)
    except Exception:
        request_logger.exception("request_failed request_id=%s method=%s path=%s duration_ms=%.1f",
                                 request_id, request.method, request.url.path,
                                 (time.perf_counter() - started) * 1000)
        raise
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Referrer-Policy", "no-referrer")
    response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
    response.headers.setdefault("X-Request-ID", request_id)
    response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
    if request.url.path.startswith(("/admin", "/v1/vault", "/vault")):
        response.headers.setdefault("Cache-Control", "no-store")
    request_logger.info("request_complete request_id=%s method=%s path=%s status=%s duration_ms=%.1f",
                        request_id, request.method, request.url.path, response.status_code,
                        (time.perf_counter() - started) * 1000)
    return response

if settings.ALLOWED_ORIGINS:
    app.add_middleware(CORSMiddleware, allow_origins=settings.ALLOWED_ORIGINS, allow_credentials=False,
                       allow_methods=["GET", "POST"],
                       allow_headers=["Authorization", "Content-Type", "X-API-Key", "api-key"])


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str = Field(min_length=1, max_length=20_000)


class ChatCompletionRequest(BaseModel):
    model: Literal["alex-agent", "deepseek-flash", "deepseek-v4-pro", "deepseek-chat", "deepseek-reasoner"] = "alex-agent"
    messages: List[ChatMessage] = Field(min_length=1, max_length=40)
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=2048, ge=1)
    stream: bool = False


class NoteCreateRequest(BaseModel):
    content: str = Field(min_length=1, max_length=100_000)
    title: Optional[str] = Field(default=None, max_length=200)
    source_book: str = Field(default="", max_length=300)
    category: str = Field(default="General", max_length=100)
    tags: Optional[List[str]] = Field(default=None, max_length=30)


def public_note(note: dict) -> dict:
    return {key: value for key, value in note.items() if key != "file_path"}


@app.get("/health")
def health_check():
    if not database_is_ready():
        return JSONResponse(status_code=503, content={"status": "unhealthy", "component": "vault"})
    return {"status": "healthy", "timestamp": int(time.time()), "version": APP_VERSION, "agent": "alex-agent"}


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)


@app.get("/")
@app.get("/v1")
def root_redirect():
    return RedirectResponse(url="/admin")


@app.get("/v1/models")
@app.get("/models")
def list_models(_: bool = Depends(require_api_token)):
    return {"object": "list", "data": [
        {"id": "alex-agent", "object": "model", "owned_by": "alex"},
        {"id": "deepseek-flash", "object": "model", "owned_by": "deepseek"},
        {"id": "deepseek-v4-pro", "object": "model", "owned_by": "deepseek"},
        {"id": "deepseek-chat", "object": "model", "owned_by": "deepseek"},
        {"id": "deepseek-reasoner", "object": "model", "owned_by": "deepseek"},
    ]}


async def handle_chat_completion(req: ChatCompletionRequest):
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(503, "AI provider is not configured")
    if sum(len(message.content) for message in req.messages) > settings.MAX_INPUT_CHARS:
        raise HTTPException(413, "Conversation is too large")
    if req.max_tokens > settings.MAX_OUTPUT_TOKENS:
        raise HTTPException(422, f"max_tokens cannot exceed {settings.MAX_OUTPUT_TOKENS}")
    messages = [message.model_dump() for message in req.messages]
    if req.model == "alex-agent":
        if req.stream:
            return StreamingResponse(run_agent_stream(messages, req.max_tokens), media_type="text/event-stream",
                                     headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"})
        return JSONResponse(content=await run_agent_completion(messages, req.max_tokens))
    model = req.model
    if req.stream:
        return StreamingResponse(call_deepseek_stream(messages, model, req.temperature, req.max_tokens),
                                 media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"})
    return JSONResponse(content=await call_deepseek_non_stream(messages, model, req.temperature, req.max_tokens))


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
@app.post("/v1")
@app.post("/")
async def chat_completions(req: ChatCompletionRequest, _: bool = Depends(require_api_token)):
    return await handle_chat_completion(req)


@app.get("/v1/vault/notes")
@app.get("/vault/notes")
def get_vault_notes(q: Optional[str] = None, limit: int = Query(50, ge=1, le=200), _: bool = Depends(require_api_token)):
    notes = search_notes_fts(q.strip(), limit=limit) if q and q.strip() else get_all_notes_db(limit=limit)
    return [public_note(note) for note in notes]


@app.post("/v1/vault/notes")
@app.post("/vault/notes")
def create_vault_note(req: NoteCreateRequest, _: bool = Depends(require_api_token)):
    return public_note(save_note_to_vault(req.content, req.title, req.source_book, req.category, req.tags))


@app.get("/v1/vault/graph")
@app.get("/vault/graph")
def get_vault_graph(_: bool = Depends(require_api_token)):
    return get_graph_data()


@app.get("/v1/vault/graph/image")
@app.get("/vault/graph/image")
def get_vault_graph_image(_: bool = Depends(require_api_token)):
    return Response(content=generate_kindle_graph_image(), media_type="image/png")


@app.get("/v1/vault/tags")
@app.get("/vault/tags")
def get_vault_tags(_: bool = Depends(require_api_token)):
    return get_all_tags()
