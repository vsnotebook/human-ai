from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class SpeechRecognitionInterface(ABC):
    @abstractmethod
    async def recognize(self, audio_content: bytes, language_code: str, **kwargs) -> str:
        """将音频转换为文本"""
        pass

class TranslationInterface(ABC):
    @abstractmethod
    def translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        """翻译文本"""
        pass

class TextToSpeechInterface(ABC):
    @abstractmethod
    def synthesize(self, text: str, language_code: str, **kwargs) -> str:
        """将文本转换为语音，返回音频URL"""
        pass