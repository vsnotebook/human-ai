from typing import Annotated
from fastapi import APIRouter, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from src.services.speech_service import SpeechService
from src.utils.http_session_util import get_current_user
from src.core.template import templates

router = APIRouter(prefix="/speach")
