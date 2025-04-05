import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account


os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

def transcribe_short_audio_v2(json_key_path: str, audio_file_path: str) -> None:
    # 从JSON文件加载凭据
    credentials = service_account.Credentials.from_service_account_file(json_key_path)

    # 初始化v2客户端
    client = SpeechClient(credentials=credentials)

    # 读取本地音频文件
    with open(audio_file_path, "rb") as f:
        audio_content = f.read()

    # 构建请求参数
    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            enable_spoken_punctuation=True,  # 识别口语中的标点
        )
    )

    # 发送请求
    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{credentials.project_id}/locations/global/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)
    # 输出结果
    for result in response.results:
        print(f"转录结果: {result.alternatives[0].transcript}")


# 调用示例
transcribe_short_audio_v2(
    # json_key_path="./vivid-nomad-454506.json",
    json_key_path="./vivid-nomad-454506-a3-0a3ccf718737.json",
    audio_file_path="欢迎使用阿里云-cn.mp3"
)


