from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

async def get_current_user(request: Request):
    """获取当前登录用户"""
    return request.session.get("user")

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