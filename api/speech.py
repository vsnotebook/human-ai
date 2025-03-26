from typing import Annotated
from fastapi import APIRouter, File, UploadFile, Form, Request, Depends, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from services.firestore_service import FirestoreService
from services.speech_service import SpeechService
from utils.auth import get_current_user

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    user = await get_current_user(request)
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "current_user": user,
        },
    )

@router.get("/transcribe-audio", response_class=HTMLResponse)
async def upload_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)
    
    return templates.TemplateResponse(
        "transcribe-audio.html",
        {
            "request": request,
            "current_user": user,
            "trial_count": user.get("trial_count", 10) if user else 10,
            "trial_seconds": user.get("trial_seconds", 60) if user else 60,
            "subscription": None,  # 这里可以添加订阅信息
        },
    )

@router.post("/transcribe")
async def transcribe_audio(
    file: UploadFile = File(...),
    language_code: Annotated[str, Form()] = "en-US",
    model: Annotated[str, Form()] = "latest_long",
):
    try:
        if not file.content_type.startswith("audio/"):
            return JSONResponse(
                content={"error": "Invalid file type. Only audio files are allowed."},
                status_code=400,
            )

        audio_content = await file.read()
        transcription = await SpeechService.transcribe(audio_content, language_code)
        print(transcription)
        return {"transcription": transcription}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


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
    # if await FirestoreService.create_user(username, email, password):
    if FirestoreService.create_user(username, email, password):
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse(
        "register.html",
        {
            "request": request,
            "error": "用户名或邮箱已存在"
        }
    )

@router.get("/admin/users", response_class=HTMLResponse)
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


@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = await get_current_user(request)
    if not user or user.get('role') != 'admin':
        return RedirectResponse(url="/", status_code=302)
    
    # 获取统计数据
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