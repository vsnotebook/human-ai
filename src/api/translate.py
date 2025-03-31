from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from google.cloud import translate_v2 as translate
from src.core.template import templates
from src.utils.http_session_util import get_current_user

# from dependencies import get_current_user

router = APIRouter()


class TranslateRequest(BaseModel):
    text: str
    target: str = "en"
    source: Optional[str] = "auto"


@router.get("/user/translate", response_class=HTMLResponse)
async def translate_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "user/translate.html",
        {"request": request, "active_page": "translate", "current_user": current_user}
    )


@router.post("/api/translate")
async def translate_api(translate_req: TranslateRequest, current_user=Depends(get_current_user)):
    text = translate_req.text
    target = translate_req.target
    source = translate_req.source

    if not text:
        raise HTTPException(status_code=400, detail="没有提供文本")

    try:
        # 如果源语言是自动检测，则不指定源语言
        result = translate_text(target, text, source if source != "auto" else None)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def translate_text(target: str, text: str, source: str = None) -> dict:
    """Translates text into the target language.

    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """
    translate_client = translate.Client()

    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    if source:
        result = translate_client.translate(text, target_language=target, source_language=source)
    else:
        result = translate_client.translate(text, target_language=target)

    return result
