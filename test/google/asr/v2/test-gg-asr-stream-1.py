# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START speech_transcribe_streaming_v2]
import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types

# PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")

PROJECT_ID = "human-ai-454609"
os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

def transcribe_streaming_v2(
    stream_file: str,
) -> cloud_speech_types.StreamingRecognizeResponse:
    """Transcribes audio from an audio file stream using Google Cloud Speech-to-Text API.
    Args:
        stream_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.wav"
    Returns:
        list[cloud_speech_types.StreamingRecognizeResponse]: A list of objects.
            Each response includes the transcription results for the corresponding audio segment.
    """
    # Instantiates a client
    client = SpeechClient()

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
        language_codes=["en-US"],
        model="long",
    )
    streaming_config = cloud_speech_types.StreamingRecognitionConfig(
        config=recognition_config
    )
    config_request = cloud_speech_types.StreamingRecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        streaming_config=streaming_config,
    )

    def requests(config: cloud_speech_types.RecognitionConfig, audio: list) -> list:
        yield config
        yield from audio

    # Transcribes the audio into text
    responses_iterator = client.streaming_recognize(
        requests=requests(config_request, audio_requests)
    )
    responses = []
    for response in responses_iterator:
        responses.append(response)
        for result in response.results:
            print(f"Transcript: {result.alternatives[0].transcript}")

    return responses


# [END speech_transcribe_streaming_v2]


if __name__ == "__main__":
    # transcribe_streaming_v2("../resources/audio.wav")
    # transcribe_streaming_v2("../resources/Open Google Chrome.wav")
    transcribe_streaming_v2("../resources/p_41508289_310.mp3")

