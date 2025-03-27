from fastapi import Request
from typing import Optional

async def get_current_user(request: Request) -> Optional[dict]:
    user = request.session.get("user")
    return user if user else None