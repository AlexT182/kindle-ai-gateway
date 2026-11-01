import time
import uuid
import logging
import json
import asyncio
from contextlib import asynccontextmanager
from typing import Any, AsyncIterator, Dict, List, Literal, Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse, Response, StreamingResponse
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from app.agent import call_deepseek_non_stream, call_deepseek_stream
from app.agent_runtime import run_agent_completion, run_agent_stream
from app.auth import require_api_token
from app.config import APP_VERSION, settings
from app.db import database_is_ready, record_usage_event
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
    request.state.request_id = request_id
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


def usage_fields(data: Dict[str, Any]) -> Dict[str, int]:
    usage = data.get("usage") or {}
    def safe_int(value: Any) -> int:
        try:
            return max(0, int(value or 0))
        except (TypeError, ValueError):
            return 0

    prompt = safe_int(usage.get("prompt_tokens") or usage.get("input_tokens"))
    completion = safe_int(usage.get("completion_tokens") or usage.get("output_tokens"))
    total = safe_int(usage.get("total_tokens") or (prompt + completion))
    return {"prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total}


async def persist_usage(request_id: str, model: str, stream: bool, status: str,
                        started: float, usage: Optional[Dict[str, Any]] = None, tool_calls: int = 0) -> None:
    fields = usage_fields({"usage": usage or {}})
    try:
        await run_in_threadpool(
            record_usage_event,
            request_id,
            model,
            stream,
            status,
            (time.perf_counter() - started) * 1000,
            fields["prompt_tokens"],
            fields["completion_tokens"],
            fields["total_tokens"],
            tool_calls,
        )
    except Exception:
        request_logger.warning("usage_persist_failed request_id=%s", request_id, exc_info=True)


async def metered_stream(source: AsyncIterator[str], request_id: str, model: str,
                         started: float, metrics: Optional[Dict[str, Any]] = None) -> AsyncIterator[str]:
    observed_usage: Dict[str, Any] = {}
    status = "success"
    try:
        async for chunk in source:
            if chunk.startswith("data: "):
                raw = chunk[6:].strip()
                if raw and raw != "[DONE]":
                    try:
                        payload = json.loads(raw)
                        if isinstance(payload.get("usage"), dict):
                            observed_usage = payload["usage"]
                    except (json.JSONDecodeError, AttributeError):
                        pass
            yield chunk
    except asyncio.CancelledError:
        status = "cancelled"
        raise
    except Exception:
        status = "error"
        raise
    finally:
        metrics = metrics or {}
        await persist_usage(request_id, model, True, status, started,
                            metrics.get("usage") or observed_usage,
                            int(metrics.get("tool_calls") or 0))


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


async def handle_chat_completion(req: ChatCompletionRequest, request: Request):
    if not settings.DEEPSEEK_API_KEY:
        raise HTTPException(503, "AI provider is not configured")
    if sum(len(message.content) for message in req.messages) > settings.MAX_INPUT_CHARS:
        raise HTTPException(413, "Conversation is too large")
    if req.max_tokens > settings.MAX_OUTPUT_TOKENS:
        raise HTTPException(422, f"max_tokens cannot exceed {settings.MAX_OUTPUT_TOKENS}")
    messages = [message.model_dump() for message in req.messages]
    request_id = request.state.request_id
    started = time.perf_counter()
    if req.model == "alex-agent":
        if req.stream:
            metrics: Dict[str, Any] = {}
            source = run_agent_stream(messages, req.max_tokens, metrics)
            return StreamingResponse(metered_stream(source, request_id, req.model, started, metrics), media_type="text/event-stream",
                                     headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"})
        try:
            data = await run_agent_completion(messages, req.max_tokens)
        except Exception:
            await persist_usage(request_id, req.model, False, "error", started)
            raise
        gateway_meta = data.pop("_gateway_meta", {})
        await persist_usage(request_id, req.model, False, "success", started, data.get("usage"),
                            int(gateway_meta.get("tool_calls") or 0))
        return JSONResponse(content=data)
    model = req.model
    if req.stream:
        source = call_deepseek_stream(messages, model, req.temperature, req.max_tokens)
        return StreamingResponse(metered_stream(source, request_id, model, started),
                                 media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Content-Type-Options": "nosniff"})
    try:
        data = await call_deepseek_non_stream(messages, model, req.temperature, req.max_tokens)
    except Exception:
        await persist_usage(request_id, model, False, "error", started)
        raise
    await persist_usage(request_id, model, False, "success", started, data.get("usage"))
    return JSONResponse(content=data)


@app.post("/v1/chat/completions")
@app.post("/chat/completions")
@app.post("/v1")
@app.post("/")
async def chat_completions(req: ChatCompletionRequest, request: Request, _: bool = Depends(require_api_token)):
    return await handle_chat_completion(req, request)


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
