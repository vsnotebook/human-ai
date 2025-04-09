import os

from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech
from google.oauth2 import service_account
PROJECT_ID = "human-ai-454609"

os.environ["http_proxy"] = "http://127.0.0.1:10808"
os.environ["https_proxy"] = "http://127.0.0.1:10808"
json_key_path="./human-ai-454609-bf84b910d612.json"
credentials = service_account.Credentials.from_service_account_file(json_key_path)
# 初始化v2客户端


def quickstart_v2_english(audio_file: str) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
    Returns:
        cloud_speech.RecognizeResponse: The response from the recognize request, containing
        the transcription results
    """
    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    # client = speech_v2.SpeechClient(client_options=client_options)
    # Instantiates a client
    client = SpeechClient()

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        language_codes=["en-US"],
        model="long",
    )

    request = cloud_speech.RecognizeRequest(
        recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response

def quickstart_v2_cn(audio_file: str) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
    Returns:
        cloud_speech.RecognizeResponse: The response from the recognize request, containing
        the transcription results
    """
    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client = speech_v2.SpeechClient(client_options=client_options)
    # Instantiates a client
    client = SpeechClient(credentials=credentials,client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        # language_codes=["en-US"],
        # language_codes=["zh-CN"],
        language_codes=["cmn-Hans-CN"],
        model="chirp",
        # model="long",
    )

    request = cloud_speech.RecognizeRequest(
        # recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


def quickstart_v2_my(audio_file: str) -> cloud_speech.RecognizeResponse:
    """Transcribe an audio file.
    Args:
        audio_file (str): Path to the local audio file to be transcribed.
    Returns:
        cloud_speech.RecognizeResponse: The response from the recognize request, containing
        the transcription results
    """
    # Reads a file as bytes
    with open(audio_file, "rb") as f:
        audio_content = f.read()

    client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
    # client = speech_v2.SpeechClient(client_options=client_options)
    # Instantiates a client
    client = SpeechClient(credentials=credentials,client_options=client_options)

    config = cloud_speech.RecognitionConfig(
        auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
        # language_codes=["en-US"],
        # language_codes=["zh-CN"],
        language_codes=["my-MM"],
        model="chirp",
        # model="long",
    )

    request = cloud_speech.RecognizeRequest(
        # recognizer=f"projects/{PROJECT_ID}/locations/global/recognizers/_",
        recognizer=f"projects/{PROJECT_ID}/locations/asia-southeast1/recognizers/_",
        config=config,
        content=audio_content,
    )

    # Transcribes the audio into text
    response = client.recognize(request=request)

    for result in response.results:
        print(f"Transcript: {result.alternatives[0].transcript}")

    return response


#quickstart_v2_english("../resources/让我来告诉你吧——是手心啊，哈哈哈.wav")
print("---------------------------------------------------------------------")
quickstart_v2_cn("../resources/让我来告诉你吧——是手心啊，哈哈哈.wav")
print("---------------------------------------------------------------------")
# quickstart_v2_my("./用户发送了一段中文文本，并希望将其翻译成缅甸文.wav")
quickstart_v2_my("../resources/用户发送了一段中文文本，并希望将其翻译成缅甸文-缅甸语.mp3")
