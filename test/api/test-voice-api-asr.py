import requests
import time
import hashlib
import hmac
import json
import argparse


def transcribe_audio(file_path, username, api_secret, language_code="zh-CN"):
    """使用API进行语音识别"""
    # 配置
    API_URL = "http://localhost:8080/external/asr"  # 根据实际部署情况修改

    # 开始计时
    start_time = time.time()

    # 读取音频文件
    with open(file_path, "rb") as f:
        audio_data = f.read()

    # 生成时间戳
    timestamp = str(int(time.time()))

    # 准备请求数据
    data = {"language_code": language_code}

    # 生成签名
    # request_body = json.dumps(data).encode('utf-8')
    request_body = json.dumps(data)
    # data_to_sign = f"{username}:{timestamp}:{request_body.decode('utf-8')}"
    data_to_sign = f"{username}:{timestamp}:{request_body}"

    signature = hmac.new(
        api_secret.encode('utf-8'),
        data_to_sign.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    # 设置请求头
    headers = {
        "X-Username": username,
        "X-Timestamp": timestamp,
        "X-Signature": signature
    }

    # 发送请求
    files = {"file": (file_path.split("/")[-1], audio_data)}
    response = requests.post(API_URL, headers=headers, files=files, data=data)

    # 计算耗时
    elapsed_time = time.time() - start_time
    
    result = response.json()
    # 添加耗时信息到返回结果
    result['elapsed_time'] = f"{elapsed_time:.2f}秒"

    return result

if __name__ == "__main__":
    file_path = r"C:\Users\vsnot\Music\audio\让我来告诉你吧——是手心啊，哈哈哈.wav"
    username = "vsfrank"
    api_secret = "f501551d0382619caf4162383174675d"
    language = "zh-CN"
    parser = argparse.ArgumentParser(description="语音识别API调用示例")
    # parser.add_argument("file", help="音频文件路径")
    # parser.add_argument("username", help="用户名")
    # parser.add_argument("api_secret", help="API密钥")
    # parser.add_argument("--language", default="zh-CN", help="语言代码 (默认: zh-CN)")

    args = parser.parse_args()

    result = transcribe_audio(file_path, username, api_secret, language)
    print("\n语音识别结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
