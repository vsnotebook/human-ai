import requests
import secrets
import time
import hashlib
import hmac
import json
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, Header

# 配置
API_URL = "https://your-api.com/api/v1/transcribe"
USERNAME = "your-username"  # 使用用户名替代API_KEY
API_SECRET = "your-api-secret"  # 用户对应的密钥

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
    API_SECRET.encode('utf-8'),
    data_to_sign.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# 设置请求头
headers = {
    "X-Username": USERNAME,  # 使用用户名作为身份标识
    "X-Timestamp": timestamp,
    "X-Signature": signature
}

# 发送请求
response = requests.post(API_URL, headers=headers, files=files, data=data)
print(response.json())


# 生成API密钥
def generate_api_secret() -> str:
    """生成32位随机API密钥"""
    return secrets.token_hex(16)  # 16字节 = 32个十六进制字符

# 验证API请求签名
def verify_api_signature(
    username: str,
    timestamp: str,
    signature: str,
    request_data: bytes,
    api_secret: str
) -> bool:
    """验证API请求签名"""
    # 检查时间戳是否在5分钟内
    current_time = int(time.time())
    request_time = int(timestamp)
    
    if abs(current_time - request_time) > 300:  # 5分钟
        return False
    
    # 重新计算签名
    data_to_sign = f"{username}:{timestamp}:{request_data.decode('utf-8') if request_data else ''}"
    expected_signature = hmac.new(
        api_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    
    # 比较签名
    return hmac.compare_digest(signature, expected_signature)

# 从请求中提取API认证信息
async def extract_api_auth(
    request: Request,
    x_username: str = Header(...),
    x_timestamp: str = Header(...),
    x_signature: str = Header(...)
) -> Tuple[str, str, str, bytes]:
    """从请求中提取API认证信息"""
    # 获取请求体
    body = await request.body()
    
    return x_username, x_timestamp, x_signature, body