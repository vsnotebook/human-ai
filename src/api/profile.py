from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from src.services.firestore_service import FirestoreService as DBService
# from src.services.mongodb_service import MongoDBService as DBService

from src.core.template import templates
from src.utils.http_session_util import get_current_user

router = APIRouter(prefix="/profile")

@router.get("", response_class=HTMLResponse)
async def profile_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "profile/index.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "profile"
        }
    )

@router.get("/password", response_class=HTMLResponse)
async def change_password_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "profile/change_password.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "profile"
        }
    )

@router.post("/password")
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...)
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    if new_password != confirm_password:
        return templates.TemplateResponse(
            "profile/change_password.html",
            {
                "request": request,
                "current_user": user,
                "active_page": "profile",
                "error": "新密码与确认密码不匹配"
            }
        )
    
    # 验证当前密码
    if not DBService.verify_password(user['id'], current_password):
        return templates.TemplateResponse(
            "profile/change_password.html",
            {
                "request": request,
                "current_user": user,
                "active_page": "profile",
                "error": "当前密码不正确"
            }
        )
    
    # 更新密码
    if await DBService.update_password(user['id'], new_password):
        return templates.TemplateResponse(
            "profile/change_password.html",
            {
                "request": request,
                "current_user": user,
                "active_page": "profile",
                "success": "密码修改成功"
            }
        )
    
    return templates.TemplateResponse(
        "profile/change_password.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "profile",
            "error": "密码修改失败，请稍后重试"
        }
    )

@router.get("/wallet", response_class=HTMLResponse)
async def wallet_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    wallet_info = await DBService.get_user_wallet(user['id'])
    transactions = await DBService.get_user_transactions(user['id'])
    
    return templates.TemplateResponse(
        "profile/wallet.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "profile",
            "wallet": wallet_info,
            "transactions": transactions
        }
    )