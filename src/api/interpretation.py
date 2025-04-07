from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from src.core.template import templates
from src.services.speech_service import SpeechService
from src.utils.http_session_util import get_current_user
from src.utils.timing_decorator import timing_decorator
from google.cloud import translate_v2 as translate
import requests

router = APIRouter()
translate_client = translate.Client()

@router.get("/user/myanmar-interpretation", response_class=HTMLResponse)
async def myanmar_interpretation_page(request: Request, current_user=Depends(get_current_user)):
    return templates.TemplateResponse(
        "user/myanmar_interpretation.html",
        {
            "request": request,
            "active_page": "myanmar_interpretation",
            "current_user": current_user,
        }
    )

@timing_decorator("语音识别")
async def speech_recognition(audio_content: bytes, source_language: str, user_id: str, filename: str) -> str:
    return await SpeechService.transcribe_by_userid(audio_content, source_language, user_id, filename)


@router.post("/myanmar-interpretation")
async def myanmar_interpretation_api(
        request: Request,
        file: UploadFile = File(...),
        source_language: str = Form(...),
        target_language: str = Form(...)
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

        # 1. 语音识别
        audio_content = await file.read()
        transcription = await speech_recognition(
            audio_content, 
            source_language, 
            user.get("id"), 
            file.filename
        )
        print("语音识别完成：" + transcription)

        # 2. 调用翻译API
        translation = translate_text(target_language, transcription,
                                     source_language.split('-')[0] if '-' in source_language else source_language)
        print("语音翻译完成：" + translation["translatedText"])

        # 3. 调用文本转语音API
        audio_url = text_to_speech(translation["translatedText"], target_language)
        print("文本转语音完成：" + audio_url)

        # 获取更新后的用户信息
        updated_user = await get_current_user(request)

        # 返回结果
        return {
            "transcription": transcription,
            "translation": translation["translatedText"],
            "audio_url": audio_url
        }

    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def translate_text(target: str, text: str, source: str = None) -> dict:
    """使用Google Translate API翻译文本"""
    if isinstance(text, bytes):
        text = text.decode("utf-8")

    # 处理语言代码格式
    if '-' in target:
        target = target.split('-')[0]  # 从zh-CN提取zh

    if source and '-' in source:
        source = source.split('-')[0]  # 从zh-CN提取zh

    # 发送翻译请求
    if source and source != "auto":
        result = translate_client.translate(text, target_language=target, source_language=source)
    else:
        result = translate_client.translate(text, target_language=target)

    return result

def text_to_speech(text: str, language_code: str) -> str:
    """使用TTS API将文本转换为语音"""
    # 处理语言代码格式
    if '-' in language_code:
        language_code = language_code.split('-')[0]  # 从zh-CN提取zh

    # 根据语言选择对应的语音
    voice_map = {
        "zh": "zh-CN-XiaoxiaoNeural",
        "my": "my-MM-ThihaNeural",
        "en": "en-US-JennyNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural"
    }

    voice = voice_map.get(language_code, "zh-CN-XiaoxiaoNeural")

    # 准备请求数据
    form_data = {
        "text": text,
        "voice": voice,
        "rate": "+0%",
        "pitch": "+0Hz",
        "volume": "+0%"
    }

    try:
        # 发送TTS请求
        base_url = "http://47.120.55.3:5000"
        audio_base_url = "https://tts.51685168.xyz"
        synthesize_url = f"{base_url}/api/synthesize"
        
        response = requests.post(
            synthesize_url,
            data=form_data,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            raise Exception(f"语音合成请求失败，状态码: {response.status_code}")

        result = response.json()
        if result["status"] != "success":
            raise Exception(result.get("message", "语音合成失败"))

        return f"{audio_base_url}{result['download_url']}"

    except Exception as e:
        raise Exception(f"TTS服务请求错误: {str(e)}")