from typing import Dict, Type
from src.infrastructure.audio.interfaces import SpeechRecognitionInterface, TranslationInterface, TextToSpeechInterface
from src.infrastructure.audio.adapters.google_adapter import GoogleSpeechAdapter, GoogleTranslateAdapter, GoogleTTSAdapter
from src.infrastructure.audio.adapters.aliyun_adapter import AliyunSpeechAdapter, AliyunTranslateAdapter, AliyunTTSAdapter
from src.core.config import settings

class AudioServiceFactory:
    # 服务提供商映射
    _speech_adapters: Dict[str, Type[SpeechRecognitionInterface]] = {
        "google": GoogleSpeechAdapter,
        "aliyun": AliyunSpeechAdapter,
    }
    
    _translate_adapters: Dict[str, Type[TranslationInterface]] = {
        "google": GoogleTranslateAdapter,
        "aliyun": AliyunTranslateAdapter,
    }
    
    _tts_adapters: Dict[str, Type[TextToSpeechInterface]] = {
        "google": GoogleTTSAdapter,
        "aliyun": AliyunTTSAdapter,
    }
    
    @classmethod
    def get_speech_service(cls, provider: str = "google") -> SpeechRecognitionInterface:
        """获取语音识别服务"""
        adapter_class = cls._speech_adapters.get(provider.lower())
        if not adapter_class:
            raise ValueError(f"不支持的语音识别服务提供商: {provider}")
            
        # 根据提供商获取配置
        if provider.lower() == "aliyun":
            return adapter_class()
        else:
            return adapter_class()
    
    @classmethod
    def get_translate_service(cls, provider: str = "google") -> TranslationInterface:
        """获取翻译服务"""
        adapter_class = cls._translate_adapters.get(provider.lower())
        if not adapter_class:
            raise ValueError(f"不支持的翻译服务提供商: {provider}")
            
        # 根据提供商获取配置
        if provider.lower() == "aliyun":
            return adapter_class(
                access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
                access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
            )
        else:
            return adapter_class()
    
    @classmethod
    def get_tts_service(cls, provider: str = "google") -> TextToSpeechInterface:
        """获取文本转语音服务"""
        adapter_class = cls._tts_adapters.get(provider.lower())
        if not adapter_class:
            raise ValueError(f"不支持的文本转语音服务提供商: {provider}")
            
        # 根据提供商获取配置
        if provider.lower() == "aliyun":
            return adapter_class(
                access_key_id=settings.ALIYUN_ACCESS_KEY_ID,
                access_key_secret=settings.ALIYUN_ACCESS_KEY_SECRET
            )
        else:
            return adapter_class()