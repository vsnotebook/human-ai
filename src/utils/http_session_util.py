from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN
from src.db.mongodb import db

async def get_current_user(request: Request):
    """获取当前登录用户"""
    return request.session.get("user")

# 在现有的get_current_user函数中添加force_refresh参数
async def get_current_user2(request: Request, force_refresh: bool = False):
    """
    从会话中获取当前用户信息
    
    Args:
        request: 请求对象
        force_refresh: 是否强制从数据库刷新用户信息
        
    Returns:
        用户信息或None
    """
    session = request.session
    user_id = session.get("user_id")
    
    if not user_id:
        return None
    
    # 如果不需要强制刷新且会话中已有用户信息，则直接返回
    if not force_refresh and "user" in session:
        return session.get("user")
    
    # 从数据库获取最新的用户信息
    # db = await get_db()
    user = await db.users.find_one({"_id": user_id})

    if user:
        # 更新会话中的用户信息
        session["user"] = user
        return user

    # 如果用户不存在，清除会话
    session.pop("user_id", None)
    session.pop("user", None)
    return None

async def admin_required(request: Request):
    """验证用户是否为管理员"""
    user = await get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="未登录",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.get("role") != "admin":
        raise HTTPException(
            status_code=HTTP_403_FORBIDDEN,
            detail="权限不足，需要管理员权限",
        )
    return user