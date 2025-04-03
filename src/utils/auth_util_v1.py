import jwt
import time
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional
from fastapi import Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# 配置
JWT_SECRET = "your-jwt-secret-key"  # 生产环境应使用环境变量
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION = 24  # 小时
API_KEYS = {}  # 在实际应用中，这应该存储在数据库中

security = HTTPBearer()

# 生成JWT令牌
def create_jwt_token(user_id: str, scopes: list = None) -> Dict[str, str]:
    # 生成密钥ID
    kid = secrets.token_hex(8)
    
    # 生成API密钥
    api_key = secrets.token_hex(16)
    
    # 存储API密钥（实际应用中存入数据库）
    API_KEYS[kid] = {
        "user_id": user_id,
        "api_key": api_key,
        "created_at": datetime.utcnow()
    }
    
    # 创建JWT载荷
    payload = {
        "sub": user_id,
        "scopes": scopes or [],
        "kid": kid,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION)
    }
    
    # 生成令牌
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "kid": kid,
        "api_key": api_key  # 注意：实际使用时应通过安全渠道传输
    }

# 验证JWT令牌
def decode_jwt_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")

# 生成请求签名
def generate_signature(api_key: str, timestamp: str, request_data: bytes) -> str:
    # 组合数据
    data_to_sign = f"{timestamp}:{request_data.decode('utf-8') if request_data else ''}"
    
    # 使用HMAC-SHA256生成签名
    signature = hmac.new(
        api_key.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    return signature

# 验证请求签名
def verify_signature(signature: str, api_key: str, timestamp: str, request_data: bytes) -> bool:
    # 检查时间戳是否在5分钟内
    current_time = int(time.time())
    request_time = int(timestamp)
    
    if abs(current_time - request_time) > 300:  # 5分钟
        return False
    
    # 重新计算签名
    expected_signature = generate_signature(api_key, timestamp, request_data)
    
    # 比较签名
    return hmac.compare_digest(signature, expected_signature)

# FastAPI依赖项：验证请求
async def verify_api_request(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    x_timestamp: str = Header(...),
    x_signature: str = Header(...)
) -> Dict:
    # 解析JWT令牌
    token = credentials.credentials
    payload = decode_jwt_token(token)
    
    # 获取密钥ID和用户ID
    kid = payload.get("kid")
    user_id = payload.get("sub")
    
    # 检查密钥ID是否存在
    if kid not in API_KEYS:
        raise HTTPException(status_code=401, detail="无效的密钥ID")
    
    # 获取API密钥
    api_key = API_KEYS[kid]["api_key"]
    
    # 获取请求体（这部分需要在路由函数中实现）
    # 在实际应用中，您需要获取原始请求体
    request_data = b""  # 这里应该是实际的请求体
    
    # 验证签名
    if not verify_signature(x_signature, api_key, x_timestamp, request_data):
        raise HTTPException(status_code=401, detail="签名验证失败")
    
    # 返回用户信息
    return {"user_id": user_id, "scopes": payload.get("scopes", [])}