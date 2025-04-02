import os
from typing import Annotated
from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from starlette.responses import FileResponse

from src.services.speech_service import SpeechService
from src.utils.http_session_util import get_current_user
from src.core.template import templates

router = APIRouter()


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