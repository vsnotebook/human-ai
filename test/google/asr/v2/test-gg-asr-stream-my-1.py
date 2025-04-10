import os
import time

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types, cloud_speech

# PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

PROJECT_ID = "human-ai-454609"
os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"


def transcribe_streaming_v2(
        stream_file: str,
) -> cloud_speech_types.StreamingRecognizeResponse:
    # client = SpeechClient()
    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client_options = {"api_endpoint": "us-central1-speech.googleapis.com"}
    # 初始化v2客户端
    # client = SpeechClient(credentials=credentials, client_options=client_options)
    client = SpeechClient(client_options=client_options)

    # Reads a file as bytes
    with open(stream_file, "rb") as f:
        audio_content = f.read()

    # 确保每个音频块不超过25KB (25600字节)的限制
    max_chunk_size = 25000  # 设置稍小于限制的值，以确保安全
    stream = []

    # 将音频内容分割成不超过max_chunk_size的块
    for i in range(0, len(audio_content), max_chunk_size):
        stream.append(audio_content[i:i + max_chunk_size])

    audio_requests = (
        cloud_speech_types.StreamingRecognizeRequest(audio=audio) for audio in stream
    )

    recognition_config = cloud_speech_types.RecognitionConfig(
        auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
        language_codes=["my-MM"],
        model="chirp",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            # enable_spoken_punctuation=True,  # 识别口语中的标点
        )
    )
    streaming_config = cloud_speech_types.StreamingRecognitionConfig(
        config=recognition_config
    )
    config_request = cloud_speech_types.StreamingRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/_",
        streaming_config=streaming_config,
    )
    start_time = time.time()
    def requests(config: cloud_speech_types.RecognitionConfig, audio: list) -> list:
        yield config
        yield from audio

    # Transcribes the audio into text
    responses_iterator = client.streaming_recognize(
        requests=requests(config_request, audio_requests)
    )
    responses = []

    for response in responses_iterator:
        print("=======================1")
        responses.append(response)
        for result in response.results:
            print(f"Transcript: {result.alternatives[0].transcript}")
            print(f"请求耗时: {time.time() - start_time:.2f}秒")
            start_time = time.time()
    return responses


# [END speech_transcribe_streaming_v2]


if __name__ == "__main__":
    # transcribe_streaming_v2("../resources/audio.wav")
    # transcribe_streaming_v2("../resources/Open Google Chrome.wav")
    # transcribe_streaming_v2("../resources/p_41508289_310.mp3")
    # transcribe_streaming_v2("../resources/让我来告诉你吧——是手心啊，哈哈哈.wav")
    # transcribe_streaming_v2("../resources/历代名人咏江阴_耳聆网.mp3")
    # transcribe_streaming_v2("../resources/用户发送了一段中文文本，并希望将其翻译成缅甸文-缅甸语.mp3")
    transcribe_streaming_v2("../resources/使用现代神经网络将文本转换为语音。 将其用于工作、视频编辑、商业、广告、社交网络、娱乐等。 而是粘贴您的文本，语音并下载-缅甸语.mp3")
