import os
import time

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech

import test_timing_decorator

PROJECT_ID = "human-ai-454609"
os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

@test_timing_decorator.my_timing_decorator("语音识别")
def transcribe_reuse_recognizer(
        audio_file: str,
        recognizer_id: str,
) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file using an existing recognizer.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.wav"
        recognizer_id (str): The ID of the existing recognizer to be used for transcription.
    Returns:
        cloud_speech.RecognizeResponse: The response containing the transcription results.
    """
    # Instantiates a client
    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    client = SpeechClient(client_options=client_options)

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/{recognizer_id}",
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


audio_file = "../resources/使用现代神经网络将文本转换为语音。 将其用于工作、视频编辑、商业、广告、社交网络、娱乐等。 而是粘贴您的文本，语音并下载-缅甸语.mp3"
recognizer_id = 'mymm'
start_time=time.time()
transcribe_reuse_recognizer(audio_file=audio_file, recognizer_id=recognizer_id)
print(f"请求耗时: {time.time() - start_time:.2f}秒")


