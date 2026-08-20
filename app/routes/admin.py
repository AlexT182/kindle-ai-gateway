import os
import json
from typing import Optional
from fastapi import APIRouter, Request, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.vault import (
    save_note_to_vault,
    get_all_notes_db,
    search_notes_fts,
    get_all_tags,
    get_graph_edges,
    delete_note_index
)
from app.persona import (
    get_baseline_profile,
    save_baseline_profile,
    get_evolving_memory
)
from app.scheduler import trigger_job_manual

TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(prefix="/admin", tags=["Admin Dashboard"])

def is_authenticated(request: Request) -> bool:
    session_token = request.cookies.get("admin_session")
    if not settings.AUTH_TOKEN:
        return True
    if session_token and session_token.strip().lower() == settings.AUTH_TOKEN.strip().lower():
        return True
    q_token = request.query_params.get("token", "")
    if q_token and q_token.strip().lower() == settings.AUTH_TOKEN.strip().lower():
        return True
    return False

@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"error": None}
    )

@router.post("/login")
async def process_login(request: Request, response: Response):
    token = ""
    try:
        form = await request.form()
        token = form.get("token", "")
    except Exception:
        pass
        
    if not token:
        token = request.query_params.get("token", "")

    expected = settings.AUTH_TOKEN.strip().lower() if settings.AUTH_TOKEN else ""
    if not expected or token.strip().lower() == expected:
        resp = RedirectResponse(url="/admin", status_code=303)
        resp.set_cookie("admin_session", settings.AUTH_TOKEN, max_age=86400 * 30, httponly=True)
        return resp
        
    return templates.TemplateResponse(
        request=request,
        name="admin/login.html",
        context={"error": "Auth Secret Key không chính xác. Vui lòng thử lại!"}
    )

@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/admin/login", status_code=303)
    resp.delete_cookie("admin_session")
    return resp

@router.get("", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    notes = get_all_notes_db(limit=5)
    tags = get_all_tags()
    edges = get_graph_edges()
    
    stats = {
        "notes_count": len(get_all_notes_db(limit=500)),
        "edges_count": len(edges),
        "tags_count": len(tags)
    }
    
    return templates.TemplateResponse(
        request=request,
        name="admin/dashboard.html",
        context={
            "active_tab": "dashboard",
            "title": "Bảng Điều Khiển - Kindle AI Agent",
            "stats": stats,
            "recent_notes": notes
        }
    )

@router.get("/notes", response_class=HTMLResponse)
def notes_view(request: Request, q: Optional[str] = None, tag: Optional[str] = None):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    if q and q.strip():
        notes = search_notes_fts(q.strip(), limit=50)
    else:
        notes = get_all_notes_db(limit=50)
        
    tags = get_all_tags()
    return templates.TemplateResponse(
        request=request,
        name="admin/notes.html",
        context={
            "active_tab": "notes",
            "title": "Sổ Tay Tri Thức - Kindle AI Agent",
            "notes": notes,
            "tags": tags,
            "search_q": q or "",
            "tag_q": tag or ""
        }
    )

@router.post("/notes/create")
async def create_note_admin(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    try:
        form = await request.form()
        title = form.get("title", "")
        content = form.get("content", "")
        source_book = form.get("source_book", "")
        category = form.get("category", "General")
        save_note_to_vault(content=content, title=title, source_book=source_book, category=category)
    except Exception as e:
        print(f"[Admin Note Create Error]: {e}")
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.post("/notes/delete/{note_id}")
def delete_note_admin(request: Request, note_id: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    delete_note_index(note_id)
    return RedirectResponse(url="/admin/notes", status_code=303)

@router.get("/graph", response_class=HTMLResponse)
def graph_view(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse(
        request=request,
        name="admin/graph.html",
        context={
            "active_tab": "graph",
            "title": "3D Knowledge Graph View - Kindle AI Agent"
        }
    )

@router.get("/persona", response_class=HTMLResponse)
def persona_view(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    profile = get_baseline_profile()
    memory = get_evolving_memory()
    
    return templates.TemplateResponse(
        request=request,
        name="admin/persona.html",
        context={
            "active_tab": "persona",
            "title": "Cá Tính AI - Kindle AI Agent",
            "profile": profile,
            "memory": memory,
            "message": None
        }
    )

@router.post("/persona/save")
async def save_persona_admin(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
        
    try:
        form = await request.form()
        user_name = form.get("user_name", "Alex")
        user_role = form.get("user_role", "Product Manager")
        thinking_models = form.get("thinking_models", "")
        communication_rules = form.get("communication_rules", "")
        
        models_list = [m.strip() for m in thinking_models.splitlines() if m.strip()]
        rules_list = [r.strip() for r in communication_rules.splitlines() if r.strip()]
        
        profile_data = {
            "user_name": user_name.strip(),
            "user_role": user_role.strip(),
            "thinking_models": models_list,
            "communication_rules": rules_list,
            "favorite_authors": ["Don Norman", "Dan Olsen", "Peter Thiel", "Nassim Taleb"]
        }
        save_baseline_profile(profile_data)
        memory = get_evolving_memory()
        return templates.TemplateResponse(
            request=request,
            name="admin/persona.html",
            context={
                "active_tab": "persona",
                "title": "Cá Tính AI - Kindle AI Agent",
                "profile": profile_data,
                "memory": memory,
                "message": "Đã lưu cấu hình cá tính Persona thành công!"
            }
        )
    except Exception as e:
        print(f"[Admin Persona Save Error]: {e}")
        return RedirectResponse(url="/admin/persona", status_code=303)

@router.get("/scheduler", response_class=HTMLResponse)
def scheduler_view(request: Request, msg: Optional[str] = None):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse(
        request=request,
        name="admin/scheduler.html",
        context={
            "active_tab": "scheduler",
            "title": "Bộ Lập Lịch - Kindle AI Agent",
            "message": msg
        }
    )

@router.post("/scheduler/run/{job_name}")
async def run_scheduler_job_manual(request: Request, job_name: str):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    res = await trigger_job_manual(job_name)
    return RedirectResponse(url=f"/admin/scheduler?msg={res}", status_code=303)

@router.get("/mcp", response_class=HTMLResponse)
def mcp_view(request: Request):
    if not is_authenticated(request):
        return RedirectResponse(url="/admin/login")
    return templates.TemplateResponse(
        request=request,
        name="admin/mcp.html",
        context={
            "active_tab": "mcp",
            "title": "Hệ Sinh Thái MCP Tools - Kindle AI Agent"
        }
    )
