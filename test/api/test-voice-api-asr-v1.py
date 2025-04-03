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