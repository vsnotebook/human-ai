from typing import Annotated
from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import os
from services.speech_service import SpeechService

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    message = "It's running!"
    service = os.environ.get('K_SERVICE', 'Unknown service')
    revision = os.environ.get('K_REVISION', 'Unknown revision')

    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "message": message,
            "Service": service,
            "Revision": revision,
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
        return {"transcription": transcription}

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/transcribe-audio", response_class=HTMLResponse)
async def upload_page(request: Request):
    return templates.TemplateResponse("transcribe-audio.html", {"request": request})