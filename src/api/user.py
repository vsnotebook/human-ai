from fastapi import APIRouter, Form, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse  # 添加 JSONResponse

# from src.config.payment_config import SUBSCRIPTION_PLANS
from src.config.plans import SUBSCRIPTION_PLANS
from src.models.user import User
from src.services.firestore_service import FirestoreService as DBService
# from src.services.mongodb_service import MongoDBService as DBService
from src.core.template import templates
from src.utils.http_session_util import get_current_user

router = APIRouter(prefix="/user")


@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    usage_stats = await DBService.get_user_usage_stats(user['id'])
    return templates.TemplateResponse(
        "user/dashboard.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "dashboard",
            "stats": usage_stats
        }
    )


@router.get("/subscriptions", response_class=HTMLResponse)
async def user_subscriptions(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    subscriptions = await DBService.get_user_subscriptions(user['id'])
    return templates.TemplateResponse(
        "user/subscriptions.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "subscriptions",
            "subscriptions": subscriptions
        }
    )

@router.get("/asr", response_class=HTMLResponse)
async def subscription_plans(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "user/asr.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "asr"
        }
    )


@router.get("/tts", response_class=HTMLResponse)
async def subscription_plans(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "user/tts.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "tts"
        }
    )



@router.get("/plans", response_class=HTMLResponse)
async def subscription_plans(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "user/plans.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "plans"
        }
    )


@router.get("/orders", response_class=HTMLResponse)
async def user_orders(request: Request):
    user = await get_current_user(request)
    print("==================================3")
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    orders = await DBService.get_user_orders(user['id'])
    return templates.TemplateResponse(
        "user/orders.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "orders",
            "orders": orders
        }
    )


@router.get("/checkout", response_class=HTMLResponse)
async def checkout(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    plan_id = request.query_params.get("plan")
    if not plan_id or plan_id not in SUBSCRIPTION_PLANS:
        return RedirectResponse(url="/user/plans", status_code=302)

    return templates.TemplateResponse(
        "user/checkout.html",
        {
            "request": request,
            "current_user": user,
            "plan": SUBSCRIPTION_PLANS[plan_id]
        }
    )


@router.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "user/profile.html",  # 修改模板路径
        {
            "request": request,
            "current_user": user,
            "active_page": "profile"
        }
    )


@router.get("/balance", response_class=HTMLResponse)
async def user_balance(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # 获取用户余额信息
    balance = await DBService.get_user_balance(user['id'])
    
    return templates.TemplateResponse(
        "user/balance.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "balance",
            "balance": balance
        }
    )


@router.post("/change-password")
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
        return JSONResponse(content={
            "success": False,
            "error": "新密码与确认密码不匹配"
        })

    # 验证当前密码
    if not DBService.verify_password(user['id'], current_password):
        return JSONResponse(content={
            "success": False,
            "error": "当前密码不正确"
        })

    # 更新密码
    if await DBService.update_password(user['id'], new_password):
        return JSONResponse(content={
            "success": True,
            "message": "密码修改成功"
        })

    return JSONResponse(content={
        "success": False,
        "error": "密码修改失败，请稍后重试"
    })


@router.post("/recharge")
async def recharge(
        request: Request,
        amount: int = Form(...)
):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    # 处理充值逻辑
    if await DBService.add_user_balance(user['id'], amount):
        return templates.TemplateResponse(
            "user/profile.html",
            {
                "request": request,
                "current_user": user,
                "active_page": "profile",
                "success": "充值成功"
            }
        )

    return templates.TemplateResponse(
        "user/profile.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "profile",
            "error": "充值失败，请稍后重试"
        }
    )


# 在用户路由中添加API密钥管理功能

@router.get("/api-keys", response_class=HTMLResponse)
async def api_keys_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # 获取用户的API密钥
    api_keys = DBService.get_user_api_keys(user.get("id"))
    
    return templates.TemplateResponse(
        "user/api-keys.html",
        {
            "request": request,
            "current_user": user,
            "api_keys": api_keys
        }
    )

@router.post("/api-keys/create")
async def create_api_key(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # 创建新的API密钥
    api_key = DBService.create_api_key(user.get("id"))
    
    return RedirectResponse(url="/user/api-keys", status_code=302)

@router.post("/api-keys/{key_id}/deactivate")
async def deactivate_api_key(request: Request, key_id: str):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    # 停用API密钥
    success = DBService.deactivate_api_key(key_id, user.get("id"))
    
    return RedirectResponse(url="/user/api-keys", status_code=302)


@router.get("/myanmar-interpretation", response_class=HTMLResponse)
async def myanmar_interpretation(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "user/myanmar_interpretation.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "myanmar-interpretation"
        }
    )
