from fastapi import APIRouter, Form, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
# from src.services.firestore_service import FirestoreService as DBService
from src.services.mongodb_service import MongoDBService as DBService
from src.core.template import templates

router = APIRouter()

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})

@router.post("/register")
async def register(
    request: Request,
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    # 创建用户并初始化余额
    user_id = DBService.create_user(username, email, password)
    if user_id:
        # 创建用户余额记录，包含赠送额度
        await DBService.create_user_balance(user_id, {
            "asr_balance": 60,  # 赠送1分钟语音识别 (单位:秒)
            "tts_balance": 500,  # 赠送500个字符合成
            "text_translation_balance": 0,
            "voice_translation_balance": 0
        })
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "auth/register.html",
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
    user = DBService.verify_user(username, password)
    # user = await FirestoreService.authenticate_user(username, password)
    if not user:
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "error": "用户名或密码错误"}
        )

    # 设置session
    request.session["user"] = user

    # 根据用户角色重定向到不同页面
    if user.get('role') == 'admin':
        return RedirectResponse(url="/admin/dashboard", status_code=302)
    else:
        return RedirectResponse(url="/user/dashboard", status_code=302)

@router.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)