import requests

# 准备请求数据
# url = "http://your-domain.com/transcribe"
url = "http://127.0.0.1:8080/transcribe"
files = {
    'file': ('audio.mp3', open('path/to/audio.mp3', 'rb'), 'audio/mpeg')
}
data = {
    'language_code': 'zh-CN',
    'model': 'latest_long'
}

# 发送请求
response = requests.post(url, files=files, data=data)

# 处理响应
if response.status_code == 200:
    result = response.json()
    print(f"转写结果: {result['transcription']}")
else:
    print(f"请求失败: {response.json()['error']}")