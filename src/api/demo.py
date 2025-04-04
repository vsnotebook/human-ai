from typing import Annotated
from typing import Optional

from fastapi import APIRouter, Request, Depends
from fastapi import File, UploadFile, Form
from fastapi.responses import JSONResponse
from fastapi.responses import RedirectResponse

from src.core.template import templates
from src.services.db.demo_firestore_service import DemoFirestoreService as DemoService
# from src.services.db.demo_mongo_service import DemoMongoService as DemoService
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

    # 获取并更新试用记录
    trial_record = await DemoService.update_trial_count(client_ip)
    if not trial_record:
        return RedirectResponse(
            url="/register?message=error",
            status_code=302
        )

    # 检查是否超过试用次数
    if trial_record["count"] >= MAX_TRIAL_COUNT:
        return RedirectResponse(
            url="/register?message=trial_exceeded",
            status_code=302
        )

    return None


@router.get("/try-demo")
async def try_demo(
        request: Request,
        # redirect: Optional[RedirectResponse] = Depends(check_trial_count),
        current_user=Depends(get_current_user)
):
    # if redirect:
    #     return redirect

    # 获取IP的试用次数
    client_ip = request.client.host
    trial_record = await DemoService.get_trial_record(client_ip)
    trial_count = trial_record["count"] if trial_record else 0

    return templates.TemplateResponse(
        "voice_recognition.html",
        {
            "request": request,
            "current_user": current_user,
            "trial_count": trial_count
        }
    )


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
