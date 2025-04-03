import requests
import secrets
import time
import hashlib
import hmac
import json
from typing import Dict, Optional, Tuple
from fastapi import Request, HTTPException, Header

# 生成API密钥
def generate_api_secret() -> str:
    """生成32位随机API密钥"""
    return secrets.token_hex(16)  # 16字节 = 32个十六进制字符

# 验证API请求签名
def verify_api_signature(
    username: str,
    timestamp: str,
    signature: str,
    form_data: dict,
    api_secret: str
) -> bool:
    """验证API请求签名"""
    # 检查时间戳是否在5分钟内
    current_time = int(time.time())
    request_time = int(timestamp)
    
    if abs(current_time - request_time) > 300:  # 5分钟
        return False
    
    # 重新计算签名 - 使用表单数据
    # 注意：这里我们只使用language_code等表单字段，不包括文件内容
    data_to_sign = f"{username}:{timestamp}:{json.dumps(form_data)}"
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
) -> Tuple[str, str, str]:
    """从请求中提取API认证信息"""
    # 不再尝试读取请求体，因为它可能已经被消费
    return x_username, x_timestamp, x_signature