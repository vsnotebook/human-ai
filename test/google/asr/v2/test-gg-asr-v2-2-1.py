import os
import time

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account

os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

# json_key_path="./vivid-nomad-454506.json",
# json_key_path = "./vivid-nomad-454506-a3-0a3ccf718737.json"
# json_key_path = "./human-ai-454609-bf84b910d612.json"
# 从JSON文件加载凭据
# credentials = service_account.Credentials.from_service_account_file(json_key_path)
PROJECT_ID = "human-ai-454609"
def transcribe_short_audio_v2(audio_file_path: str) -> None:
    # 初始化v2客户端
    client = SpeechClient(PROJECT_ID)

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
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)
    # 输出结果
    for result in response.results:
        print(f"转录结果: {result.alternatives[0].transcript}")


def quickstart_v2_english(audio_file: str) -> cloud_speech.RecognizeResponse:
    # 初始化v2客户端
    client = SpeechClient(PROJECT_ID)

    with open(audio_file, "rb") as f:
        audio_content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            # enable_spoken_punctuation=True,  # 识别口语中的标点
        )
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        content=audio_content,
    )

    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


def quickstart_v2_cn(audio_file: str) -> cloud_speech.RecognizeResponse:
    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # 初始化v2客户端
    client = SpeechClient(client_options=client_options)

    with open(audio_file, "rb") as f:
        audio_content = f.read()

    # client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client = speech_v2.SpeechClient(client_options=client_options)
    # Instantiates a client
    # client = SpeechClient(client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["cmn-Hans-CN"],
        model="chirp"
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


def quickstart_v2_cn2(audio_file: str) -> cloud_speech.RecognizeResponse:
    # region = "us-central1"
    # region = "europe-west4"
    region = "asia-southeast1"
    client_options = {"api_endpoint": f"{region}-speech.googleapis.com"}
    # 初始化v2客户端
    client = SpeechClient(client_options=client_options)




    with open(audio_file, "rb") as f:
        audio_content = f.read()

    # client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client = speech_v2.SpeechClient(client_options=client_options)
    # Instantiates a client
    # client = SpeechClient(client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["cmn-Hans-CN"],
        # model="chirp_2",
        model="chirp",
        # Enable automatic punctuation
        # enable_automatic_punctuation=True,
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            # enable_spoken_punctuation=True,  # 识别口语中的标点
        )
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/{region}/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


def quickstart_v2_my(audio_file: str) -> cloud_speech.RecognizeResponse:
    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # 初始化v2客户端
    client = SpeechClient(client_options=client_options)

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    # client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client = SpeechClient(client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["my-MM"],
        model="chirp",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            # enable_spoken_punctuation=True,  # 识别口语中的标点
        )
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


def quickstart_v2_my2(audio_file: str) -> cloud_speech.RecognizeResponse:
    region = "us-central1"
    client_options = {"api_endpoint": f"{region}-speech.googleapis.com"}
    # 初始化v2客户端
    client = SpeechClient(client_options=client_options)

    with open(audio_file, "rb") as f:
        audio_content = f.read()

    # client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client = SpeechClient(client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["my-MM"],
        model="chirp",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            # enable_spoken_punctuation=True,  # 识别口语中的标点
        )
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/{region}/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


# 调用示例
# transcribe_short_audio_v2(audio_file_path="欢迎使用阿里云-cn.mp3")
# quickstart_v2_english("./让我来告诉你吧——是手心啊，哈哈哈.wav")
print("---------------------------------------------------------------------")
# quickstart_v2_cn("../resources/让我来告诉你吧——是手心啊，哈哈哈.wav")

# quickstart_v2_cn("../resources/第五十六条 经营者违反本法规定.wav")
# quickstart_v2_cn2("../resources//让我来告诉你吧——是手心啊，哈哈哈.wav")
# quickstart_v2_cn2("../resources/第五十六条 经营者违反本法规定.wav")
print("---------------------------------------------------------------------")
# quickstart_v2_my("../resources//用户发送了一段中文文本，并希望将其翻译成缅甸文.wav")
# quickstart_v2_my("../resources//用户发送了一段中文文本，并希望将其翻译成缅甸文-缅甸语.mp3")
# quickstart_v2_my2("../resources//用户发送了一段中文文本，并希望将其翻译成缅甸文-缅甸语.mp3")
start_time=time.time()
quickstart_v2_my("../resources/使用现代神经网络将文本转换为语音。 将其用于工作、视频编辑、商业、广告、社交网络、娱乐等。 而是粘贴您的文本，语音并下载-缅甸语.mp3")
print(f"\n程序执行时间: {time.time() - start_time:.2f} 秒")

start_time=time.time()
quickstart_v2_my2("../resources/使用现代神经网络将文本转换为语音。 将其用于工作、视频编辑、商业、广告、社交网络、娱乐等。 而是粘贴您的文本，语音并下载-缅甸语.mp3")
print(f"\n程序执行时间: {time.time() - start_time:.2f} 秒")

