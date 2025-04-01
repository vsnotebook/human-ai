from typing import Optional

from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, EmailStr, Field
from starlette.responses import RedirectResponse

from src.core.template import templates
# from src.services.firestore_service import FirestoreService as DBService
from src.services.mongodb_service import MongoDBService as DBService
from src.utils.http_session_util import get_current_user, admin_required

router = APIRouter(prefix="/admin")


# 用户管理页面
@router.get("/users", response_class=HTMLResponse)
async def admin_users_page(request: Request, user=Depends(admin_required)):
    users = DBService.get_all_users(user.get('id'))
    return templates.TemplateResponse(
        "admin/users.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "users",
            "users": users
        }
    )


# 获取单个用户信息
@router.get("/users/{user_id}")
async def get_user(user_id: str, user=Depends(admin_required)):
    try:
        user_data = await DBService.get_user_by_id(user_id)
        if not user_data:
            raise HTTPException(status_code=404, detail="用户不存在")

        # 处理日期时间对象，转换为字符串
        if 'created_at' in user_data and user_data['created_at']:
            user_data['created_at'] = user_data['created_at'].isoformat()

        return user_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户数据失败: {str(e)}")


# 用户模型
class UserUpdate(BaseModel):
    username: str = Field(..., min_length=2)
    email: EmailStr
    password: Optional[str] = None
    role: str = "user"
    trial_count: int = 10


# 更新用户
@router.put("/users/{user_id}")
async def update_user(user_id: str, user_data: UserUpdate, user=Depends(admin_required)):
    # 直接传递用户数据，密码加密在FirestoreService中处理
    result = await DBService.update_user(user_id, user_data.dict(exclude_unset=True))
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在或更新失败")
    return {"message": "用户更新成功"}


# 创建用户
@router.post("/users")
async def create_user(user_data: UserUpdate, user=Depends(admin_required)):
    if not user_data.password:
        raise HTTPException(status_code=400, detail="新用户必须设置密码")

    # 密码加密在FirestoreService中处理
    result = await DBService.create_user_by_admin(
        username=user_data.username,
        email=user_data.email,
        password=user_data.password,
        role=user_data.role,
        trial_count=user_data.trial_count
    )

    if not result:
        raise HTTPException(status_code=400, detail="创建用户失败，可能用户名或邮箱已存在")
    return {"message": "用户创建成功"}


# 删除用户
@router.delete("/users/{user_id}")
async def delete_user(user_id: str, user=Depends(admin_required)):
    result = await DBService.delete_user(user_id)
    if not result:
        raise HTTPException(status_code=404, detail="用户不存在或删除失败")
    return {"message": "用户删除成功"}


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    user = await get_current_user(request)
    if not user or user.get('role') != 'admin':
        return RedirectResponse(url="/", status_code=302)

    stats = await DBService.get_dashboard_stats()
    activities = await DBService.get_recent_activities()

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "current_user": user,
            "active_page": "dashboard",
            "stats": stats,
            "activities": activities
        }
    )
