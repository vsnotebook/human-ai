from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
import os
import tempfile
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import translate_v2 as translate
import requests
import json
import uuid
import urllib3
from src.core.template import templates
from src.services.speech_service import SpeechService
from src.utils.http_session_util import get_current_user

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

router = APIRouter()

# 语音识别客户端
speech_client = speech.SpeechClient()
# 翻译客户端
translate_client = translate.Client()


@router.get("/user/voice-translate", response_class=HTMLResponse)
async def voice_translate_page(request: Request, current_user=Depends(get_current_user)):
    # 这里可以添加用户订阅信息等
    return templates.TemplateResponse(
        "user/voice_translate.html",
        {
            "request": request,
            "active_page": "voice_translate",
            "current_user": current_user,
            "remaining_minutes": 60,  # 示例值，实际应从用户数据中获取
            "trial_count": 3,  # 示例值
            "trial_seconds": 180  # 示例值
        }
    )


@router.post("/voice-translate")
async def voice_translate_api(
        request: Request,
        file: UploadFile = File(...),
        source_language: str = Form(...),
        target_language: str = Form(...),
        model: str = Form("long")
):
    try:
        # 获取当前用户
        user = await get_current_user(request)
        if not user:
            return JSONResponse(
                content={"error": "用户未登录，请先登录"},
                status_code=401,
            )

        try:
            if not file.content_type.startswith("audio/"):
                return JSONResponse(
                    content={"error": "无效的文件类型。只允许音频文件。"},
                    status_code=400,
                )

            # 1. 调用语音识别API
            audio_content = await file.read()
            # 传递用户ID以便扣除余额
            transcription = await SpeechService.transcribe(audio_content, source_language, user.get("_id"))
            print("语音识别完成：" + transcription)

            # 2. 调用翻译API
            translation = translate_text(target_language, transcription,
                                         source_language.split('-')[0] if '-' in source_language else source_language)
            print("语音翻译完成：" + translation["translatedText"])

            # 3. 调用文本转语音API
            audio_url = text_to_speech(translation["translatedText"], target_language)
            print("文本转语音完成：" + audio_url)

            # 获取更新后的用户信息
            # updated_user = await get_current_user(request, force_refresh=True)
            updated_user = await get_current_user(request)

            # 返回结果
            return {
                "transcription": transcription,
                "translation": translation["translatedText"],
                "detected_language": translation.get("detectedSourceLanguage", ""),
                "audio_url": audio_url,
                "remaining_seconds": updated_user.get("remaining_audio_seconds", 0)
            }

        finally:
            # 清理临时文件
            pass

    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def transcribe_audio(file_path: str, language_code: str, model: str) -> str:
    """使用Google Speech-to-Text API转写音频"""

    # 读取音频文件
    with open(file_path, "rb") as audio_file:
        content = audio_file.read()

    # 配置识别请求
    audio = speech.RecognitionAudio(content=content)

    # 处理语言代码格式
    if '-' in language_code:
        language_code = language_code  # 如zh-CN
    else:
        # 映射简单语言代码到完整格式
        language_map = {
            "zh": "zh-CN",
            "en": "en-US",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "fr": "fr-FR",
            "de": "de-DE",
            "my": "my-MM"
        }
        language_code = language_map.get(language_code, language_code)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code,
        model=model,
        enable_automatic_punctuation=True,
    )

    # 发送请求
    response = speech_client.recognize(config=config, audio=audio)

    # 处理响应
    transcript = ""
    for result in response.results:
        transcript += result.alternatives[0].transcript

    return transcript


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
        # 发送TTS请求，禁用SSL验证
        audio_base_url = "https://tts.51685168.xyz"
        base_url = "http://47.120.55.3:5000"
        synthesize_url = f"{base_url}/api/synthesize"
        response = requests.post(
            synthesize_url,
            data=form_data,
            verify=False,  # 禁用SSL验证
            timeout=30  # 设置超时时间
        )

        if response.status_code != 200:
            raise Exception(f"语音合成请求失败，状态码: {response.status_code}")

        result = response.json()

        if result["status"] != "success":
            raise Exception(result.get("message", "语音合成失败"))

        audio_url = f"{audio_base_url}{result['download_url']}"
        print(audio_url)
        # 返回音频URL
        return audio_url
    
    except requests.exceptions.SSLError as e:
        # 处理SSL错误
        print(f"TTS服务SSL错误: {str(e)}")
        # 尝试使用HTTP而非HTTPS
        try:
            response = requests.post(
                "http://tts.51685168.xyz/api/synthesize", 
                data=form_data,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"语音合成请求失败，状态码: {response.status_code}")
                
            result = response.json()
            
            if result["status"] != "success":
                raise Exception(result.get("message", "语音合成失败"))
                
            return f"http://tts.51685168.xyz{result['download_url']}"
        except Exception as http_e:
            raise Exception(f"TTS服务连接失败: {str(http_e)}")
    
    except requests.exceptions.Timeout:
        raise Exception("TTS服务请求超时")
    
    except requests.exceptions.ConnectionError:
        raise Exception("无法连接到TTS服务器")
    
    except Exception as e:
        raise Exception(f"TTS服务请求错误: {str(e)}")