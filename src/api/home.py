import os
from datetime import datetime, timedelta
from typing import Annotated
from typing import Optional

from fastapi import APIRouter, File, UploadFile, Form, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.responses import FileResponse

from src.core.template import templates
from src.db.mongodb import db
from src.services.speech_service import SpeechService
from src.utils.http_session_util import get_current_user

router = APIRouter()

MAX_TRIAL_COUNT = 3


async def check_trial_count(request: Request) -> Optional[RedirectResponse]:
    # 如果已登录，直接通过
    if request.session.get("user_id"):
        return None

    # 获取客户端IP
    client_ip = request.client.host
    print(f"client_ip: {client_ip}")

    # 从MongoDB获取IP试用记录
    trial_collection = db.trial_records
    trial_record = trial_collection.find_one({"ip": client_ip})

    # 如果没有记录或记录已过期（7天），创建/重置记录
    current_time = datetime.utcnow()
    if not trial_record or (current_time - trial_record["last_try"]) > timedelta(days=14):
        trial_record = {
            "ip": client_ip,
            "count": 0,
            "last_try": current_time,
            "created_at": current_time
        }

    # 检查是否超过试用次数
    if trial_record["count"] >= MAX_TRIAL_COUNT:
        return RedirectResponse(
            url="/register?message=trial_exceeded",
            status_code=302
        )

    # 更新试用次数
    trial_collection.update_one(
        {"ip": client_ip},
        {
            "$set": {
                "last_try": current_time,
                "count": trial_record["count"] + 1
            },
            "$setOnInsert": {"created_at": current_time}
        },
        upsert=True
    )

    return None


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


# 在注册其他路由之前添加这段代码
@router.get('/favicon.ico')
async def favicon():
    file_path = "src/static/images/favicon.ico"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return FileResponse("src/static/images/favicon.ico", status_code=404)


@router.get("/transcribe-audio", response_class=HTMLResponse)
async def upload_page(request: Request):
    user = await get_current_user(request)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "user/transcribe-audio.html",
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
        request: Request,
        file: UploadFile = File(...),
        language_code: Annotated[str, Form()] = "en-US",
        model: Annotated[str, Form()] = "latest_long",
):
    try:
        # 获取当前用户
        user = await get_current_user(request)
        if not user:
            return JSONResponse(
                content={"error": "用户未登录，请先登录"},
                status_code=401,
            )

        if not file.content_type.startswith("audio/"):
            return JSONResponse(
                content={"error": "无效的文件类型。只允许音频文件。"},
                status_code=400,
            )

        # 获取文件名
        file_name = file.filename

        audio_content = await file.read()

        # 传递用户ID以便扣除余额并记录使用情况
        transcription = await SpeechService.transcribe_by_userid(audio_content, language_code, user.get("id"),
                                                                 file_name)
        print(transcription)

        # 获取更新后的用户信息
        updated_user = await get_current_user(request)

        # 从user_balance表获取最新的ASR余额
        # balance = db.user_balance.find_one({"user_id": user.get("id")})
        # remaining_seconds = balance.get("asr_balance", 0) if balance else 0

        return {
            "transcription": transcription,
            "remaining_seconds": updated_user.get("remaining_audio_seconds", 0)
        }

    except ValueError as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/transcribe_trial")
async def transcribe_trial(
        request: Request,
        file: UploadFile = File(...),
        language_code: Annotated[str, Form()] = "en-US",
        redirect: Optional[RedirectResponse] = Depends(check_trial_count),
        model: Annotated[str, Form()] = "latest_long",
):
    # 如果需要重定向，直接返回重定向响应
    if redirect:
        return RedirectResponse(
            url="/register?message=trial_exceeded",
            status_code=303  # 使用 303 See Other 状态码
        )
    
    try:
        if not file.content_type.startswith("audio/"):
            return JSONResponse(
                content={"error": "无效的文件类型。只允许音频文件。"},
                status_code=400,
            )

        # 获取文件名
        file_name = file.filename

        audio_content = await file.read()

        # 传递用户ID以便扣除余额并记录使用情况
        transcription = await SpeechService.transcribe(audio_content, language_code)
        print(transcription)

        # 获取更新后的用户信息
        # updated_user = await get_current_user(request)

        # 从user_balance表获取最新的ASR余额
        # balance = db.user_balance.find_one({"user_id": user.get("id")})
        # remaining_seconds = balance.get("asr_balance", 0) if balance else 0

        return {
            "transcription": transcription,
            # "remaining_seconds": updated_user.get("remaining_audio_seconds", 0)
        }

    except ValueError as e:
        print(str(e))
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        print(str(e))
