from typing import Dict, Any, Optional

import requests
from google.cloud import speech_v2 as speech
from google.cloud import translate_v2 as translate
from google.cloud.speech_v2.types import cloud_speech

from src.config.language_config import LANGUAGE_CONFIG
from src.core.config import settings
from src.infrastructure.audio.interfaces import SpeechRecognitionInterface, TranslationInterface, TextToSpeechInterface


class GoogleSpeechAdapter(SpeechRecognitionInterface):
    def __init__(self):
        self.client = speech.SpeechClient()

    # @staticmethod
    # async def recognize(self, audio_content: bytes, language_code: str, **kwargs) -> str:
    async def recognize(self, audio_content: bytes, language_code: str, **kwargs) -> str:
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
            recognizer=f"projects/{settings.PROJECT_ID}/locations/{region}/recognizers/_",
            config=config,
            content=audio_content,
        )

        response = speech_client.recognize(request=request)

        transcription = ""
        for result in response.results:
            for alternative in result.alternatives:
                transcription += alternative.transcript

        return transcription



class GoogleTranslateAdapter(TranslationInterface):
    def __init__(self):
        self.client = translate.Client()

    def translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """使用Google Translate API翻译文本"""
        if isinstance(text, bytes):
            text = text.decode("utf-8")

        # 处理语言代码格式
        if '-' in target_language:
            target_language = target_language.split('-')[0]

        if source_language and '-' in source_language:
            source_language = source_language.split('-')[0]

        # 发送翻译请求
        if source_language and source_language != "auto":
            result = self.client.translate(text, target_language=target_language, source_language=source_language)
        else:
            result = self.client.translate(text, target_language=target_language)

        return result


class GoogleTTSAdapter(TextToSpeechInterface):
    def synthesize(self, text: str, language_code: str, **kwargs) -> str:
        # 这里使用的是第三方TTS服务，而不是Google的TTS
        # 处理语言代码格式
        if '-' in language_code:
            language_code = language_code.split('-')[0]

        # 根据语言选择对应的语音
        voice_map = {
            "zh": "zh-CN-XiaoxiaoNeural",
            "my": "my-MM-ThihaNeural",
            "en": "en-US-JennyNeural",
            "ja": "ja-JP-NanamiNeural",
            "ko": "ko-KR-SunHiNeural",
            "fr": "fr-FR-DeniseNeural",
            "de": "de-DE-KatjaNeural"
        }

        voice = voice_map.get(language_code, "zh-CN-XiaoxiaoNeural")

        # 准备请求数据
        form_data = {
            "text": text,
            "voice": voice,
            "rate": "+0%",
            "pitch": "+0Hz",
            "volume": "+0%"
        }

        try:
            # 发送TTS请求
            base_url = "http://47.120.55.3:5000"
            audio_base_url = "https://tts.51685168.xyz"
            synthesize_url = f"{base_url}/api/synthesize"

            response = requests.post(
                synthesize_url,
                data=form_data,
                verify=False,
                timeout=30
            )

            if response.status_code != 200:
                raise Exception(f"语音合成请求失败，状态码: {response.status_code}")

            result = response.json()
            if result["status"] != "success":
                raise Exception(result.get("message", "语音合成失败"))

            return f"{audio_base_url}{result['download_url']}"

        except Exception as e:
            raise Exception(f"TTS服务请求错误: {str(e)}")
