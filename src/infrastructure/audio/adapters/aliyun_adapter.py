from dashscope.audio.asr import Recognition
import wave

from src.infrastructure.audio.interfaces import SpeechRecognitionInterface, TranslationInterface, TextToSpeechInterface
from http import HTTPStatus
import dashscope
import json
import tempfile
import os
from typing import Dict, Any, Optional

class AliyunSpeechAdapter(SpeechRecognitionInterface):
    def __init__(self):
        self.app_key = "sk-196bc2b54b444440962781ef844e7720"
        dashscope.api_key = self.app_key
    
    async def recognize(self, audio_content: bytes, language_code: str, **kwargs) -> str:
        try:
            print("使用 aliyun 语音识别")
            
            # 创建临时文件并写入音频数据
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
                temp_file.write(audio_content)
                temp_file_path = temp_file.name
            
            try:
                # 读取WAV文件信息
                with wave.open(temp_file_path, 'rb') as wav_file:
                    sample_rate = wav_file.getframerate()
                    channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()

                print(f"音频信息: 采样率={sample_rate}, 声道数={channels}, 采样宽度={sample_width}")
                
                # 动态创建识别实例
                recognition = Recognition(
                    model='paraformer-realtime-v2',
                    format='wav',
                    sample_rate=sample_rate,
                    language_hints=['zh', 'my', 'en'],
                    callback=None
                )
                
                # 使用临时文件路径调用识别API
                result = recognition.call(temp_file_path)
            finally:
                # 删除临时文件
                if os.path.exists(temp_file_path):
                    print(temp_file_path)
                    os.unlink(temp_file_path)
            
            if result.status_code == HTTPStatus.OK:
                # 提取识别文本
                if result.output and result.output.get('sentence'):
                    sentence_ = result.output['sentence']
                    text_ = sentence_[0]['text']
                    # TODO  返回多个 要合在一起。
                    print("阿里云识别结果:  "+text_)
                    return text_
                return ""
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