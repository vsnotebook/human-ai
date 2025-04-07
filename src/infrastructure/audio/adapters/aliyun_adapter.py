from dashscope.audio.asr import Recognition

from src.infrastructure.audio.interfaces import SpeechRecognitionInterface, TranslationInterface, TextToSpeechInterface
from http import HTTPStatus
import dashscope
import json
from typing import Dict, Any, Optional


class AliyunSpeechAdapter(SpeechRecognitionInterface):
    def __init__(self):
        # self.app_key = app_key  # API Key
        self.app_key = "sk-196bc2b54b444440962781ef844e7720"  # API Key
        dashscope.api_key = self.app_key
        self.recognition = Recognition(
            model='paraformer-realtime-v2',
            format='wav',
            sample_rate=16000,
            language_hints=['zh', 'my', 'en'],  # 支持中文、缅甸语和英语
            callback=None
        )
    
    async def recognize(self, audio_content: bytes, language_code: str, **kwargs) -> str:
        try:
            print("使用 aliyun 语音识别")
            # 调用阿里云语音识别API
            result = self.recognition.call(audio_content)
            
            if result.status_code == HTTPStatus.OK:
                return result.get_sentence()
            else:
                raise Exception(f"语音识别失败: {result.message}")
                
        except Exception as e:
            raise Exception(f"阿里云语音识别错误: {str(e)}")

class AliyunTranslateAdapter(TranslationInterface):
    def __init__(self, access_key_id=None, access_key_secret=None, region_id="cn-hangzhou"):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.region_id = region_id
        # self.client = AcsClient(self.access_key_id, self.access_key_secret, self.region_id)
    
    def translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        # 处理语言代码格式
        lang_map = {
            "zh": "zh",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
            "fr": "fr",
            "de": "de",
            "my": "my"  # 假设阿里云支持缅甸语
        }
        
        target = lang_map.get(target_language.split('-')[0], target_language)
        source = lang_map.get(source_language.split('-')[0], source_language) if source_language else "auto"
        
        # request = TranslateGeneralRequest()
        request = None
        request.set_FormatType("text")
        request.set_SourceLanguage(source)
        request.set_TargetLanguage(target)
        request.set_SourceText(text)
        
        try:
            response = self.client.do_action_with_exception(request)
            result = json.loads(response)
            return {
                "translatedText": result.get("Data", {}).get("Translated", ""),
                "detectedSourceLanguage": source
            }
        except Exception as e:
            raise Exception(f"阿里云翻译错误: {str(e)}")

class AliyunTTSAdapter(TextToSpeechInterface):
    def __init__(self, access_key_id=None, access_key_secret=None):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        # 初始化阿里云语音合成客户端
    
    def synthesize(self, text: str, language_code: str, **kwargs) -> str:
        # 这里实现阿里云语音合成的逻辑
        # 由于需要阿里云账号和相关配置，这里只提供框架
        
        # 示例代码
        # 1. 准备请求参数
        # 2. 发送请求到阿里云API
        # 3. 解析响应，获取音频URL
        
        # 模拟返回结果
        return "https://example.com/audio.mp3"