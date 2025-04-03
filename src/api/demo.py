from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Request, Depends
from fastapi.responses import RedirectResponse
from src.core.template import templates
from src.utils.http_session_util import get_current_user
from src.db.mongodb import db

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
    if not trial_record or (current_time - trial_record["last_try"]) > timedelta(days=7):
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
    # trial_collection.update_one(
    #     {"ip": client_ip},
    #     {
    #         "$set": {
    #             "last_try": current_time,
    #             "count": trial_record["count"] + 1
    #         },
    #         "$setOnInsert": {"created_at": current_time}
    #     },
    #     upsert=True
    # )
    
    return None

@router.get("/try-demo")
async def try_demo(
    request: Request,
    # redirect: Optional[RedirectResponse] = Depends(check_trial_count),
    current_user = Depends(get_current_user)
):
    # if redirect:
    #     return redirect
    
    # 获取IP的试用次数
    client_ip = request.client.host
    trial_record = db.trial_records.find_one({"ip": client_ip})
    trial_count = trial_record["count"] if trial_record else 0
    
    return templates.TemplateResponse(
        "voice_recognition.html",
        {
            "request": request,
            "current_user": current_user,
            "trial_count": trial_count
        }
    )