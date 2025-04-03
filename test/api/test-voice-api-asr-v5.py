import requests
import time
import hashlib
import hmac
import json

# 配置
API_URL = "http://localhost:8080/external/asr"
USERNAME = "vsfrank"  # 您的用户名
API_SECRET = "f501551d0382619caf4162383174675d"  # 请替换为您的实际API密钥

# 准备请求
file_path = r"C:\Users\vsnot\Music\audio\让我来告诉你吧——是手心啊，哈哈哈.wav"
with open(file_path, "rb") as f:
    audio_data = f.read()

# 生成时间戳
timestamp = str(int(time.time()))

# 准备请求数据
# form_data = {"language_code": "zh-CN", "model": "latest_long"}
form_data = {"language_code": "zh-CN"}

# 生成签名 - 修改为使用表单数据
data_to_sign = f"{USERNAME}:{timestamp}:{json.dumps(form_data)}"
signature = hmac.new(
    API_SECRET.encode('utf-8'),
    data_to_sign.encode('utf-8'),
    hashlib.sha256
).hexdigest()

# 设置请求头
headers = {
    "X-Username": USERNAME,
    "X-Timestamp": timestamp,
    "X-Signature": signature
}

# 发送请求
files = {
    "file": (
        "audio.wav",
        audio_data,
        "audio/wav"  # 指定content_type为audio/wav
    )
}
response = requests.post(API_URL, headers=headers, files=files, data=form_data)
print(response)
if response.status_code == 200:
    print(response.json())
else:
    print(f"错误: {response.text}")