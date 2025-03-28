from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from src.services.firestore_service import FirestoreService
from src.core.template import templates

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    if FirestoreService.create_user(username, email, password):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "error": "用户名或邮箱已存在"
        }
    )

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    user = FirestoreService.verify_user(username, password)
    if user:
        request.session["user"] = user
        return RedirectResponse(url="/", status_code=302)
    return templates.TemplateResponse(
        "login.html",
        {
            "request": request,
            "error": "用户名或密码错误"
        }
    )

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)