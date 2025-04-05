import os
import os

import re

from google.cloud import storage
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
import time

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types, cloud_speech

# PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

PROJECT_ID = "human-ai-454609"
os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

def transcribe_batch_gcs_input_inline_output_v2(
    audio_uri: str,
) -> cloud_speech.BatchRecognizeResults:
    """Transcribes audio from a Google Cloud Storage URI using the Google Cloud Speech-to-Text API.
        The transcription results are returned inline in the response.
    Args:
        audio_uri (str): The Google Cloud Storage URI of the input audio file.
            E.g., gs://[BUCKET]/[FILE]
    Returns:
        cloud_speech.BatchRecognizeResults: The response containing the transcription results.
    """
    # Instantiates a client
    # client = SpeechClient()
    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # 初始化v2客户端
    # client = SpeechClient(credentials=credentials, client_options=client_options)
    client = SpeechClient(client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["cmn-Hans-CN"],
        model="chirp",
        features=cloud_speech.RecognitionFeatures(
            enable_automatic_punctuation=True,  # 自动添加标点
            # enable_spoken_punctuation=True,  # 识别口语中的标点
            enable_word_time_offsets=True
        )
    )

    file_metadata = cloud_speech.BatchRecognizeFileMetadata(uri=audio_uri)

    request = cloud_speech.BatchRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/_",
        config=config,
        files=[file_metadata],
        recognition_output_config=cloud_speech.RecognitionOutputConfig(
            inline_response_config=cloud_speech.InlineOutputConfig(),
        ),
    )

    # 添加开始时间记录
    start_time = time.time()

    # Transcribes the audio into text
    operation = client.batch_recognize(request=request)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=120)

    # 计算总耗时
    total_time = time.time() - start_time
    print(f"\n识别总耗时: {total_time:.2f} 秒")

    if audio_uri not in response.results:
        print(f"错误：未能获取到 {audio_uri} 的识别结果")
        return None

    transcript = response.results[audio_uri].transcript
    if not transcript.results:
        print(f"警告：{audio_uri} 的识别结果为空，可能原因：")
        print("1. 音频文件可能是空的")
        print("2. 音频质量太差")
        print("3. 音频格式不支持")
        return None

    for result in transcript.results:
        if not result.alternatives:
            print(f"警告：结果中没有可用的转录内容")
            continue

        if not result.alternatives:
            print(f"警告：结果中没有可用的转录内容")
            continue

        print(f"Transcript: {result.alternatives[0].transcript}")
        # 如果需要查看更多信息，可以取消下面的注释
        # print(f"Confidence: {result.alternatives[0].confidence}")

    return response.results[audio_uri].transcript


# [END speech_transcribe_streaming_v2]


if __name__ == "__main__":
    # transcribe_streaming_v2("../resources/audio.wav")
    # transcribe_streaming_v2("../resources/Open Google Chrome.wav")
    # transcribe_streaming_v2("../resources/p_41508289_310.mp3")
    # transcribe_streaming_v2("../resources/让我来告诉你吧——是手心啊，哈哈哈.wav")
    # transcribe_streaming_v2("../resources/历代名人咏江阴_耳聆网.mp3")
    # transcribe_batch_gcs_input_inline_output_v2("gs://[BUCKET]/[FILE]")
    # transcribe_batch_gcs_input_inline_output_v2("gs://voice-audio-1001/徐秀娟故居讲解词.mp3")
    transcribe_batch_gcs_input_inline_output_v2("gs://voice-audio-1001/test.mp3")
    # transcribe_batch_gcs_input_inline_output_v2("../resources/第五十六条 经营者违反本法规定.wav")
