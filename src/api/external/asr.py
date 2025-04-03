from fastapi import APIRouter, File, UploadFile, Form, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated, Optional

from src.services.speech_service import SpeechService
from src.services.mongodb_service import MongoDBService as DBService
from src.utils.auth_util import extract_api_auth, verify_api_signature

router = APIRouter(prefix="/external")


@router.post("/asr")
async def external_asr_v1(
        file: UploadFile = File(...),
        language_code: Annotated[str, Form()] = "en-US",
        auth_info: tuple = Depends(extract_api_auth)
):
    username, timestamp, signature = auth_info

    try:
        # 获取用户的API密钥
        api_secret = DBService.get_api_secret(username)
        if not api_secret:
            raise HTTPException(status_code=401, detail="无效的用户名")

        # 准备表单数据用于签名验证
        form_data = {
            "language_code": language_code
        }

        # 验证签名
        if not verify_api_signature(username, timestamp, signature, form_data, api_secret):
            raise HTTPException(status_code=401, detail="签名验证失败")

        # 获取用户ID
        user = DBService.get_user_by_username(username)
        if not user:
            raise HTTPException(status_code=401, detail="用户不存在")

        # 检查文件类型 - 修改文件类型检查逻辑
        file_content_type = file.content_type or ""
        allowed_types = ["audio/", "application/octet-stream"]
        is_allowed = any(file_content_type.startswith(t) for t in allowed_types)
        
        if not is_allowed and not file.filename.lower().endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            return JSONResponse(
                content={"error": "无效的文件类型。只允许音频文件。"},
                status_code=400,
            )

        # 获取文件名和内容
        file_name = file.filename
        audio_content = await file.read()

        # 调用语音识别服务
        transcription = await SpeechService.transcribe_by_userid(
            audio_content,
            language_code,
            user.get("id"),
            file_name
        )

        # 获取更新后的用户余额
        updated_user = DBService.get_user_by_id(user.get("id"))

        return {
            "success": True,
            "transcription": transcription
        }

    except ValueError as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    except HTTPException as e:
        return JSONResponse(content={"error": e.detail}, status_code=e.status_code)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)