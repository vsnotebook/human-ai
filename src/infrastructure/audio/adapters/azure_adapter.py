import azure.cognitiveservices.speech as speechsdk
import tempfile
import time
import os
import wave
from typing import Dict, Any, Optional

from src.infrastructure.audio.interfaces import SpeechRecognitionInterface, TranslationInterface, TextToSpeechInterface
from http import HTTPStatus

class AzureSpeechAdapter(SpeechRecognitionInterface):
    def __init__(self, subscription_key=None, region="southeastasia"):
        # self.subscription_key = subscription_key or os.environ.get('SPEECH_KEY')
        self.subscription_key = os.getenv('SPEECH_KEY')
        self.region = region
        self.endpoint = f"https://{region}.api.cognitive.microsoft.com/"
        print(subscription_key)
    
    async def recognize(self, audio_content: bytes, language_code: str, **kwargs) -> str:
        try:
            print("使用 Azure 语音识别")
            print(language_code)

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
                
                # 配置语音识别
                speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, endpoint=self.endpoint)
                speech_config.speech_recognition_language = language_code
                
                # 配置音频输入
                audio_config = speechsdk.audio.AudioConfig(filename=temp_file_path)
                
                # 创建语音识别器
                speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                
                # 执行语音识别
                result = speech_recognizer.recognize_once_async().get()
                
                # 确保在尝试删除文件前释放所有资源
                del speech_recognizer
                del audio_config
                del speech_config
                
            finally:
                # 添加延迟以确保文件不再被使用
                time.sleep(0.5)
                
                # 删除临时文件
                try:
                    if os.path.exists(temp_file_path):
                        print(f"尝试删除临时文件: {temp_file_path}")
                        os.unlink(temp_file_path)
                        print(f"删除临时文件: {temp_file_path}完成")
                except Exception as e:
                    print(f"删除临时文件失败: {str(e)}，这不会影响识别结果")
            
            # 处理结果
            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                recognized_text = result.text
                print("Azure识别结果: " + recognized_text)
                return recognized_text
            elif result.reason == speechsdk.ResultReason.NoMatch:
                print(f"无法识别语音: {result.no_match_details}")
                return ""
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                if cancellation_details.reason == speechsdk.CancellationReason.Error:
                    print("Error details: {}".format(cancellation_details.error_details))
                print(result.cancellation_details.error_details)
                raise Exception(f"语音识别已取消: {cancellation_details.reason}")
                
        except Exception as e:
            raise Exception(f"Azure语音识别错误: {str(e)}")

class AzureTranslateAdapter(TranslationInterface):
    def __init__(self, subscription_key=None, region="southeastasia"):
        self.subscription_key = subscription_key or os.environ.get('TRANSLATOR_KEY')
        self.region = region
    
    def translate(self, text: str, target_language: str, source_language: Optional[str] = None) -> Dict[str, Any]:
        # 处理语言代码格式
        lang_map = {
            "zh": "zh-Hans",
            "en": "en",
            "ja": "ja",
            "ko": "ko",
            "fr": "fr",
            "de": "de",
            "my": "my"  # 缅甸语
        }
        
        target = lang_map.get(target_language.split('-')[0], target_language)
        source = lang_map.get(source_language.split('-')[0], source_language) if source_language else "auto"
        
        # 这里应该实现Azure翻译API的调用
        # 由于需要Azure账号和相关配置，这里只提供框架
        
        # 模拟返回结果
        return {
            "translatedText": f"[Azure翻译] {text}",
            "detectedSourceLanguage": source
        }

class AzureTTSAdapter(TextToSpeechInterface):
    def __init__(self, subscription_key=None, region="southeastasia"):
        self.subscription_key = subscription_key or os.environ.get('SPEECH_KEY')
        self.region = region
        self.endpoint = f"https://{region}.api.cognitive.microsoft.com/"
    
    def synthesize(self, text: str, language_code: str, **kwargs) -> str:
        # 这里实现Azure语音合成的逻辑
        # 由于需要Azure账号和相关配置，这里只提供框架
        
        # 示例代码
        # 1. 准备请求参数
        # 2. 发送请求到Azure API
        # 3. 解析响应，获取音频URL
        
        # 模拟返回结果
        return "https://example.com/azure_audio.mp3"