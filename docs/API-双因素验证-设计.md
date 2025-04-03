# 双因素认证方案设计
为您的语音识别API设计一个安全、优雅且简单的双因素认证方案。这个方案基于JWT令牌和请求签名相结合的方式。

## 设计概述
1. 初始认证 ：用户首先通过用户名/密码获取JWT令牌
2. API调用认证 ：使用JWT令牌+请求签名进行双重验证
## 具体流程
### 第一步：获取JWT令牌
1. 用户通过登录接口提供用户名和密码
2. 服务器验证凭据并生成JWT令牌
3. JWT令牌包含用户ID、权限范围和过期时间（通常1-24小时）
4. 服务器返回JWT令牌和一个密钥ID（kid）
### 第二步：API调用
1. 客户端准备API请求
2. 客户端使用当前时间戳和请求内容生成签名
3. 客户端在请求头中提供JWT令牌和签名信息
4. 服务器验证JWT令牌的有效性
5. 服务器验证签名的有效性
6. 如果两者都验证通过，处理请求并返回结果
## 实现建议
以下是在FastAPI中实现这个方案的关键部分：

```python
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
 ```
```

## 客户端使用示例
```python
import requests
import time
import hashlib
import hmac
import json

# 配置
API_URL = "https://your-api.com/api/v1/transcribe"
JWT_TOKEN = "your-jwt-token"
API_KEY = "your-api-key"

# 准备请求
file_path = "audio.mp3"
with open(file_path, "rb") as f:
    audio_data = f.read()

# 生成时间戳
timestamp = str(int(time.time()))

# 准备请求数据
files = {"file": ("audio.mp3", audio_data)}
data = {"language_code": "zh-CN"}

# 生成签名
request_body = json.dumps(data).encode('utf-8')
data_to_sign = f"{timestamp}:{request_body.decode('utf-8')}"
signature = hmac.new(
    API_KEY.encode('utf-8'),
    data_to_sign.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# 设置请求头
headers = {
    "Authorization": f"Bearer {JWT_TOKEN}",
    "X-Timestamp": timestamp,
    "X-Signature": signature
}

# 发送请求
response = requests.post(API_URL, headers=headers, files=files, data=data)
print(response.json())
 ```
```

## 优势
1. 安全性 ：结合JWT和请求签名提供双重保护
2. 时效性 ：JWT令牌和请求时间戳都有过期机制
3. 灵活性 ：可以为不同用户设置不同的权限范围
4. 可扩展性 ：可以轻松添加更多安全层（如IP限制）
这个方案既安全又相对简单，适合您的语音识别API服务。实际实现时，您需要根据自己的数据库结构和业务逻辑进行适当调整