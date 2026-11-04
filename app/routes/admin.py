import os
from typing import Optional

from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTask
from starlette.concurrency import run_in_threadpool

from app.auth import clear_login_failures, create_admin_session, csrf_token, is_admin_session_valid, login_allowed, record_failed_login, validate_csrf, verify_admin_password
from app.backup import cleanup_backup, create_vault_backup
from app.config import APP_VERSION, settings
from app.db import (
    activate_library_source,
    add_library_source,
    delete_library_source,
    get_library_config,
    get_library_series,
    get_library_sources,
    get_library_stats,
    set_library_config,
    get_usage_summary
)
from app.routes.library import background_sync_drive, extract_drive_id
from app.persona import get_baseline_profile, get_evolving_memory, save_baseline_profile
from app.scheduler import trigger_job_manual
from app.vault import delete_note_from_vault, get_all_notes_db, get_all_tags, get_graph_edges, save_note_to_vault, search_notes_fts

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)
router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])


def is_authenticated(request: Request) -> bool:
    return is_admin_session_valid(request.cookies.get("admin_session"))


def page_context(request: Request, **values):
    session = request.cookies.get("admin_session", "")
    return {**values, "csrf_token": csrf_token(session) if session else ""}


def require_admin(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login", status_code=303)
    return None


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="admin/login.html", context={"error": None})


@router.post("/login")
async def process_login(request: Request):
    client_ip = request.client.host if request.client else "unknown"
    if not login_allowed(client_ip):
        raise HTTPException(429, "Too many login attempts; retry later")
    form = await request.form()
    if verify_admin_password(str(form.get("password", ""))):
        clear_login_failures(client_ip)
        response = RedirectResponse(url="/admin", status_code=303)
        response.set_cookie("admin_session", create_admin_session(), max_age=settings.SESSION_MAX_AGE,
                            httponly=True, secure=True, samesite="strict", path="/admin")
        return response
    record_failed_login(client_ip)
    return templates.TemplateResponse(request=request, name="admin/login.html",
                                      context={"error": "Mật khẩu không chính xác."}, status_code=401)


@router.get("/logout")
def logout():
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session", path="/admin")
    return response


@router.get("", response_class=HTMLResponse)
@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request):
    if redirect := require_admin(request): return redirect
    notes, tags, edges = get_all_notes_db(limit=5), get_all_tags(), get_graph_edges()
    context = page_context(request, active_tab="dashboard", title="Bảng điều khiển - Kindle AI Agent",
                           stats={"notes_count": len(get_all_notes_db(limit=500)), "edges_count": len(edges), "tags_count": len(tags)},
                           recent_notes=notes, app_version=APP_VERSION, default_model=settings.DEFAULT_MODEL,
                           usage=get_usage_summary(days=7))
    return templates.TemplateResponse(request=request, name="admin/dashboard.html", context=context)


@router.get("/notes", response_class=HTMLResponse)
def notes_view(request: Request, q: Optional[str] = None, tag: Optional[str] = None):
    if redirect := require_admin(request): return redirect
    notes = search_notes_fts(q.strip(), limit=50) if q and q.strip() else get_all_notes_db(limit=50)
    context = page_context(request, active_tab="notes", title="Sổ tay tri thức - Kindle AI Agent",
                           notes=notes, tags=get_all_tags(), search_q=q or "", tag_q=tag or "")
    return templates.TemplateResponse(request=request, name="admin/notes.html", context=context)


@router.post("/notes/create")
async def create_note_admin(request: Request):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    save_note_to_vault(content=str(form.get("content", "")), title=str(form.get("title", "")),
                       source_book=str(form.get("source_book", "")), category=str(form.get("category", "General")))
    return RedirectResponse(url="/admin/notes", status_code=303)


@router.post("/notes/delete/{note_id}")
async def delete_note_admin(request: Request, note_id: str):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    delete_note_from_vault(note_id)
    return RedirectResponse(url="/admin/notes", status_code=303)


@router.get("/graph", response_class=HTMLResponse)
def graph_view(request: Request):
    if redirect := require_admin(request): return redirect
    return templates.TemplateResponse(request=request, name="admin/graph.html",
                                      context=page_context(request, active_tab="graph", title="Knowledge Graph - Kindle AI Agent"))


@router.post("/backup")
async def download_backup(request: Request):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    archive_path, temp_root = await run_in_threadpool(create_vault_backup)
    return FileResponse(
        archive_path,
        media_type="application/zip",
        filename=archive_path.name,
        background=BackgroundTask(cleanup_backup, temp_root),
    )


@router.get("/persona", response_class=HTMLResponse)
def persona_view(request: Request):
    if redirect := require_admin(request): return redirect
    return templates.TemplateResponse(request=request, name="admin/persona.html",
        context=page_context(request, active_tab="persona", title="Cá tính AI - Kindle AI Agent",
                             profile=get_baseline_profile(), memory=get_evolving_memory(), message=None))


@router.post("/persona/save")
async def save_persona_admin(request: Request):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    profile = {
        "user_name": str(form.get("user_name", "Alex")).strip()[:100],
        "user_role": str(form.get("user_role", "Product Manager")).strip()[:100],
        "thinking_models": [v.strip() for v in str(form.get("thinking_models", "")).splitlines() if v.strip()][:30],
        "communication_rules": [v.strip() for v in str(form.get("communication_rules", "")).splitlines() if v.strip()][:30],
        "favorite_authors": ["Don Norman", "Dan Olsen", "Peter Thiel", "Nassim Taleb"],
    }
    save_baseline_profile(profile)
    return RedirectResponse(url="/admin/persona", status_code=303)


@router.get("/scheduler", response_class=HTMLResponse)
def scheduler_view(request: Request, msg: Optional[str] = None):
    if redirect := require_admin(request): return redirect
    return templates.TemplateResponse(request=request, name="admin/scheduler.html",
        context=page_context(request, active_tab="scheduler", title="Bộ lập lịch - Kindle AI Agent", message=msg))


@router.post("/scheduler/run/{job_name}")
async def run_scheduler_job_manual(request: Request, job_name: str):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    result = await trigger_job_manual(job_name)
    return RedirectResponse(url=f"/admin/scheduler?msg={result}", status_code=303)


@router.get("/mcp", response_class=HTMLResponse)
def mcp_view(request: Request):
    if redirect := require_admin(request): return redirect
    return templates.TemplateResponse(request=request, name="admin/mcp.html",
        context=page_context(request, active_tab="mcp", title="Công cụ tích hợp - Kindle AI Agent"))


@router.get("/library", response_class=HTMLResponse)
def library_admin_view(request: Request):
    if redirect := require_admin(request): return redirect
    base_url = str(request.base_url).rstrip("/")
    stats = get_library_stats()
    series_list = get_library_series()
    root_folder_id = get_library_config("root_folder_id", "1eEWmqXZZmDXx4QsmsTsnjkgUMp7pe6EH")
    sync_status = get_library_config("sync_status", "idle")
    last_synced = get_library_config("last_synced_at", "")

    cache_dir = Path(settings.DATA_DIR) / "library_cache"
    cache_bytes = sum(f.stat().st_size for f in cache_dir.glob("*") if f.is_file()) if cache_dir.exists() else 0
    cache_size_str = f"{cache_bytes // 1024 // 1024} MB" if cache_bytes >= 1024 * 1024 else f"{cache_bytes // 1024} KB"

    sources = get_library_sources()
    return templates.TemplateResponse(
        request=request,
        name="admin/library.html",
        context=page_context(
            request,
            active_tab="library",
            title="Thư Viện Sách (Cloud) - Kindle AI Agent",
            stats=stats,
            series_list=series_list,
            sources=sources,
            root_folder_id=root_folder_id,
            sync_status=sync_status,
            last_synced=last_synced,
            cache_size_str=cache_size_str,
            opds_url=f"{base_url}/opds",
            web_url=f"{base_url}/library",
        )
    )


@router.post("/library/sync")
async def trigger_library_sync(request: Request, background_tasks: BackgroundTasks):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    background_tasks.add_task(background_sync_drive)
    return RedirectResponse(url="/admin/library", status_code=303)


@router.post("/library/config")
async def update_library_config(request: Request):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    raw_folder = str(form.get("root_folder_id", "")).strip()
    folder_id = extract_drive_id(raw_folder)
    if folder_id:
        set_library_config("root_folder_id", folder_id)
    return RedirectResponse(url="/admin/library", status_code=303)


@router.post("/library/sources/add")
async def add_source_route(request: Request, background_tasks: BackgroundTasks):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    title = str(form.get("title", "")).strip() or "Thư Mục Mới"
    raw_link = str(form.get("folder_link", "")).strip()
    clean_id = extract_drive_id(raw_link)
    sync_now = bool(form.get("sync_now"))

    if clean_id:
        add_library_source(title, clean_id, set_active=True)
        if sync_now:
            background_tasks.add_task(background_sync_drive, clean_id)

    return RedirectResponse(url="/admin/library", status_code=303)


@router.post("/library/sources/activate/{source_id}")
async def activate_source_route(request: Request, source_id: str, background_tasks: BackgroundTasks):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    activate_library_source(source_id)
    # Trigger background sync for the newly activated source
    folder_id = get_library_config("root_folder_id")
    if folder_id:
        background_tasks.add_task(background_sync_drive, folder_id)
    return RedirectResponse(url="/admin/library", status_code=303)


@router.post("/library/sources/delete/{source_id}")
async def delete_source_route(request: Request, source_id: str):
    if redirect := require_admin(request): return redirect
    form = await request.form()
    validate_csrf(request, form.get("csrf_token"))
    delete_library_source(source_id)
    return RedirectResponse(url="/admin/library", status_code=303)
