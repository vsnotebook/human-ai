import logging
import os

from fastapi import APIRouter, Form, Request, Response, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from google.auth.transport import requests
from google.oauth2 import id_token

from src.core.template import templates
from src.services.mongodb_service import MongoDBService as DBService

router = APIRouter()
logger = logging.getLogger("fastapi")

# 添加 Google OAuth 配置
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
print(GOOGLE_CLIENT_ID)

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


# 修改注册函数，添加API密钥创建

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
        
        # 创建默认API密钥
        DBService.create_api_key(user_id)
        
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



# 同样修改Google注册函数
@router.post("/google-register")
async def google_register(
        request: Request,
        credential: str = Form(...),
        g_csrf_token: str = Form(None)
):
    try:
        # 验证 Google token
        idinfo = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # 验证令牌
        if not idinfo:
            raise HTTPException(status_code=400, detail="Invalid token")

        # 获取用户信息
        email = idinfo['email']
        name = idinfo.get('name', email.split('@')[0])
        google_id = idinfo['sub']  # Google的唯一标识符

        # 检查用户是否已存在
        existing_user = DBService.get_user_by_email(email)
        if existing_user:
            # 如果是Google用户，直接登录
            if existing_user.get('is_google_user'):
                request.session["user"] = existing_user
                return {"success": True, "redirect_url": "/user/dashboard"}
            raise HTTPException(status_code=400, detail="该邮箱已被注册")

        # 创建新用户
        user_id = DBService.create_user(
            username=name,
            email=email,
            password=None,
            is_google_user=True
        )

        if not user_id:
            raise HTTPException(status_code=500, detail="用户创建失败")

        # 创建用户余额记录
        await DBService.create_user_balance(user_id, {
            "asr_balance": 60,
            "tts_balance": 500,
            "text_translation_balance": 0,
            "voice_translation_balance": 0
        })
        
        # 创建默认API密钥
        # DBService.create_api_key(user_id)

        # 自动登录用户
        user = DBService.get_user_by_email(email)
        request.session["user"] = user

        return {"success": True, "redirect_url": "/user/dashboard"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/google-login")
async def google_login(
        request: Request,
        credential: str = Form(...),
):
    try:
        print("---------------------------------------")
        print(GOOGLE_CLIENT_ID)
        logger.info("---------------------------------------1")
        a="bbbbbb--0"+GOOGLE_CLIENT_ID+"--aaa"
        logger.info(a)
        logger.info("---------------------------------------2")
        # 验证 Google token
        idinfo = id_token.verify_oauth2_token(
            credential,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )

        # 获取用户信息
        email = idinfo['email']

        # 获取用户
        user = DBService.get_user_by_email(email)
        if not user:
            raise HTTPException(status_code=400, detail="账号未注册，请先注册")

        # 设置session
        request.session["user"] = user

        # 直接重定向到用户中心
        return RedirectResponse(
            url="/user/dashboard",
            status_code=status.HTTP_302_FOUND
        )

    except ValueError as e:
        return RedirectResponse(
            url="/login?error=" + str(e),
            status_code=status.HTTP_302_FOUND
        )
    except Exception as e:
        return RedirectResponse(
            url="/login?error=" + str(e),
            status_code=status.HTTP_302_FOUND
        )
