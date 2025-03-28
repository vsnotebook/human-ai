from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from src.services.firestore_service import FirestoreService
from src.utils.http_session_util import get_current_user
from src.core.template import templates

router = APIRouter(prefix="/admin")

@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(request: Request):
    user = await get_current_user(request)
    if not user or user.get('role') != 'admin':
        return RedirectResponse(url="/", status_code=302)
        
    users = FirestoreService.get_all_users(user['id'])
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": user,
            "users": users
        }
    )

@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = await get_current_user(request)
    if not user or user.get('role') != 'admin':
        return RedirectResponse(url="/", status_code=302)
    
    stats = await FirestoreService.get_dashboard_stats()
    activities = await FirestoreService.get_recent_activities()
    
    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "dashboard",
            "stats": stats,
            "activities": activities
        }
    )