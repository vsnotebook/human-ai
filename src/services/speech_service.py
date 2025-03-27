from google.cloud.speech_v2.types import cloud_speech
from src.config.language_config import LANGUAGE_CONFIG

from google.cloud import speech_v2 as speech
from google.oauth2 import service_account
from src.env import PROJECT_ID, CREDENTIALS_PATH


class SpeechService:
    @staticmethod
    async def transcribe(audio_content: bytes, language_code: str) -> str:
        # 获取语言对应的区域
        # language_settings = LANGUAGE_CONFIG.get(language_code, {
        #     "name": "English (United States)",
        #     "region": "global",
        #     "model": "long",
        #     "language_code": "en-US"
        # })

        language_settings = LANGUAGE_CONFIG.get(language_code)

        language_code = language_settings['language_code']
        region = language_settings['region']
        model = language_settings['model']

        client_options = {"api_endpoint": f"{region}-speech.googleapis.com"}
        # credentials = service_account.Credentials.from_service_account_file(CREDENTIALS_PATH)
        # speech_client = speech.SpeechClient(credentials=credentials, client_options=client_options)
        speech_client = speech.SpeechClient(client_options=client_options)

        config = cloud_speech.RecognitionConfig(
            auto_decoding_config=cloud_speech.AutoDetectDecodingConfig(),
            language_codes=[language_code],
            model=model,
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

        response = speech_client.recognize(request=request)

        transcription = ""
        for result in response.results:
            for alternative in result.alternatives:
                transcription += alternative.transcript

        return transcription
