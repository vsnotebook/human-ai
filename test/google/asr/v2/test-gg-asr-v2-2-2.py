import os

from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account

PROJECT_ID = "human-ai-454609"
os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"


def transcribe_chirp_auto_detect_language(
    audio_file: str,
    region: str = "us-central1",
) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file and auto-detect spoken language using Chirp.
    Please see https://cloud.google.com/speech-to-text/v2/docs/encoding for more
    information on which audio encodings are supported.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
        region (str): The region for the API endpoint.
    Returns:
        cloud_speech.RecognizeResponse: The response containing the transcription results.
    """
    # Instantiates a client
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint=f"{region}-speech.googleapis.com",
        )
    )

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        # Set language code to auto to detect language.
        language_codes=["auto"],
        model="chirp",
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
        print(f"Detected Language: {result.language_code}")

    return response

def transcribe_chirp(
    audio_file: str,
    language_code: str = "en-US",
    region: str = "us-central1",
) -> cloud_speech.RecognizeResponse:
    """Transcribes an audio file using the Chirp model of Google Cloud Speech-to-Text API.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
            Example: "resources/audio.wav"
        language_code (str): The language code to use for transcription.
            Default is "en-US".
        region (str): The region for the API endpoint.
            Default is "us-central1".
    Returns:
        cloud_speech.RecognizeResponse: The response from the Speech-to-Text API containing
        the transcription results.
    """
    # Instantiates a client
    client = SpeechClient(
        client_options=ClientOptions(
            api_endpoint=f"{region}-speech.googleapis.com",
        )
    )

    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=[language_code],
        model="chirp",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{credentials.project_id}/locations/{region}/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response

def main():
    """
    示范如何先侦测语言，再根据侦测结果进行转录
    """
    audio_file = "开启 Google 浏览器.wav"

    print("步骤1:侦测音讯档案的语言…")
    detect_response = transcribe_chirp_auto_detect_language(audio_file)

    # 從偵測結果中獲取語言代碼
    detected_language = None
    if detect_response.results:
        detected_language = detect_response.results[0].language_code
        print(f"侦测到的语言: {detected_language}")
    else:
        # Speech-to-Text V2 supported languages
        # https://cloud.google.com/speech-to-text/v2/docs/speech-to-text-supported-languages
        print("无法侦测语言，使用预设语言（cmn-Hant-TW）")
        detected_language = "cmn-Hant-TW"

    detected_language = "en-US"
    audio_file = "../resources/Open Google Chrome.wav"

    print("\n步骤2:使用指定的语言en-US进行精确转录…")
    transcribe_response = transcribe_chirp(
        audio_file,
        language_code=detected_language
    )

    detected_language = "cmn-Hant-TW"
    audio_file = "开启 Google 浏览器.wav"

    print("\n步骤3:使用指定的语言cmn-Hant-TW进行精确转录…")
    transcribe_response = transcribe_chirp(
        audio_file,
        language_code=detected_language
    )

    print("\n转录完成!")

    return transcribe_response

if __name__ == "__main__":
    main()
