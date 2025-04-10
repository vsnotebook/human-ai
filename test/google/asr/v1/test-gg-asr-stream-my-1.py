import os
import queue
import re
import sys

from google.cloud import speech
PROJECT_ID = "human-ai-454609"
os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"

def transcribe_streaming(stream_file: str) -> speech.RecognitionConfig:
    """Streams transcription of the given audio file using Google Cloud Speech-to-Text API.
    Args:
        stream_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.raw"
    """
    client = speech.SpeechClient()

    with open(stream_file, "rb") as audio_file:
        audio_content = audio_file.read()

    # In practice, stream should be a generator yielding chunks of audio data.
    stream = [audio_content]

    requests = (
        speech.StreamingRecognizeRequest(audio_content=chunk) for chunk in stream
    )

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code="en-US",
    )

    streaming_config = speech.StreamingRecognitionConfig(config=config)

    # streaming_recognize returns a generator.
    responses = client.streaming_recognize(
        config=streaming_config,
        requests=requests,
    )

    for response in responses:
        # Once the transcription has settled, the first result will contain the
        # is_final result. The other results will be for subsequent portions of
        # the audio.
        for result in response.results:
            print(f"Finished: {result.is_final}")
            print(f"Stability: {result.stability}")
            alternatives = result.alternatives
            # The alternatives are ordered from most likely to least.
            for alternative in alternatives:
                print(f"Confidence: {alternative.confidence}")
                print(f"Transcript: {alternative.transcript}")


if __name__ == "__main__":
    # transcribe_streaming_v2("../resources/audio.wav")
    # transcribe_streaming_v2("../resources/Open Google Chrome.wav")
    # transcribe_streaming_v2("../resources/p_41508289_310.mp3")
    transcribe_streaming("../resources/Convert text to speech with modern neural networks-2.mp3")
