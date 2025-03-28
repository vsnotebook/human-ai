from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from src.core.template import templates
from src.config.plans import SUBSCRIPTION_PLANS
from src.services.firestore_service import FirestoreService
from src.utils.auth import get_current_user

router = APIRouter(prefix="/user")


@router.get("/dashboard", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    usage_stats = await FirestoreService.get_user_usage_stats(user['id'])
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

    subscriptions = await FirestoreService.get_user_subscriptions(user['id'])
    return templates.TemplateResponse(
        "user/subscriptions.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "subscriptions",
            "subscriptions": subscriptions
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
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    orders = await FirestoreService.get_user_orders(user['id'])
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
