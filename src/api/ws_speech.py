import asyncio
import json
import traceback
from abc import ABC, abstractmethod

import dashscope
import websockets
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
from fastapi import APIRouter, WebSocket
from google.cloud.speech_v2 import SpeechClient
from google.cloud.speech_v2.types import cloud_speech as cloud_speech_types

from src.services.firestore_service import FirestoreService as DBService

router = APIRouter()


# 语音识别服务的抽象基类
class SpeechRecognitionService(ABC):
    @abstractmethod
    async def initialize(self, websocket, user, language):
        pass

    @abstractmethod
    async def process_audio(self, audio_data):
        pass

    @abstractmethod
    async def stop(self):
        pass


# 阿里云语音识别服务实现
class AliSpeechRecognitionService(SpeechRecognitionService):
    def __init__(self):
        self.recognition = None
        self.callback = None
        self.is_active = False

    async def initialize(self, websocket, user, language):
        try:
            # 创建回调实例
            loop = asyncio.get_event_loop()
            self.callback = SpeechRecognitionCallback('process0', websocket, loop, user)

            # 创建识别实例
            self.recognition = Recognition(
                model='paraformer-realtime-v2',
                format='pcm',
                sample_rate=16000,
                language_hints=['zh', 'my', 'en'] if language == 'zh' else ['my', 'zh', 'en'],
                semantic_punctuation_enabled=False,
                callback=self.callback
            )

            # 启动识别
            self.recognition.start()
            self.is_active = True
            print("阿里云语音识别已启动")

            return True
        except Exception as e:
            print(f"初始化阿里云识别错误: {str(e)}")
            traceback.print_exc()
            return False

    async def process_audio(self, audio_data):
        try:
            audio_len = len(audio_data)
            print(f"阿里云识别收到音频数据: {audio_len} 字节")
            self.recognition.send_audio_frame(audio_data)
            return True
        except Exception as e:
            print(f"阿里云发送音频数据错误: {str(e)}")
            traceback.print_exc()
            return False

    async def stop(self):
        try:
            if self.recognition and self.is_active:
                self.recognition.stop()
                self.is_active = False

                # 等待所有ASR结果发送完成
                if self.callback:
                    for event in self.callback.send_events:
                        await event.wait()

                print('阿里云ASR服务已停止')
                return True
        except Exception as e:
            print(f"停止阿里云识别错误: {str(e)}")

        return False


# Google云语音识别服务实现
class GoogleSpeechRecognitionService(SpeechRecognitionService):
    def __init__(self):
        self.client = None
        self.websocket = None
        self.user = None
        self.is_active = False
        self.audio_buffer = bytearray()
        self.recognition_task = None
        self.PROJECT_ID = "human-ai-454609"  # 应从配置中获取

    async def initialize(self, websocket, user, language):
        try:
            self.websocket = websocket
            self.user = user
            self.is_active = True
            self.audio_buffer = bytearray()

            # 初始化Google Speech客户端
            client_options = {"api_endpoint": "asia-southeast1-speech.googleapis.com"}
            self.client = SpeechClient(client_options=client_options)

            print("Google云语音识别已初始化")
            return True
        except Exception as e:
            print(f"初始化Google识别错误: {str(e)}")
            traceback.print_exc()
            return False

    async def process_audio(self, audio_data):
        try:
            if not self.is_active:
                return False

            # 将音频数据添加到缓冲区
            self.audio_buffer.extend(audio_data)
            print(f"Google识别收到音频数据: {len(audio_data)} 字节，缓冲区大小: {len(self.audio_buffer)} 字节")
            return True
        except Exception as e:
            print(f"Google处理音频数据错误: {str(e)}")
            traceback.print_exc()
            return False

    async def stop(self):
        try:
            if not self.is_active:
                return True

            self.is_active = False

            # 启动异步任务处理累积的音频数据
            if len(self.audio_buffer) > 0:
                self.recognition_task = asyncio.create_task(
                    self._process_buffered_audio(bytes(self.audio_buffer))
                )
                await self.recognition_task

            print('Google ASR服务已停止')
            return True
        except Exception as e:
            print(f"停止Google识别错误: {str(e)}")
            traceback.print_exc()
            return False

    async def _process_buffered_audio(self, audio_content):
        try:
            # 确保每个音频块不超过25KB的限制
            max_chunk_size = 25000
            stream = []

            # 将音频内容分割成不超过max_chunk_size的块
            for i in range(0, len(audio_content), max_chunk_size):
                stream.append(audio_content[i:i + max_chunk_size])

            audio_requests = (
                cloud_speech_types.StreamingRecognizeRequest(audio=audio)
                for audio in stream
            )

            # 配置识别参数
            recognition_config = cloud_speech_types.RecognitionConfig(
                auto_decoding_config=cloud_speech_types.AutoDetectDecodingConfig(),
                language_codes=["my-MM"],  # 缅甸语
                model="chirp",
                features=cloud_speech_types.RecognitionFeatures(
                    enable_automatic_punctuation=True,
                )
            )

            streaming_config = cloud_speech_types.StreamingRecognitionConfig(
                config=recognition_config
            )

            config_request = cloud_speech_types.StreamingRecognizeRequest(
                recognizer=f"projects/{self.PROJECT_ID}/locations/asia-southeast1/recognizers/_",
                streaming_config=streaming_config,
            )

            def requests(config, audio):
                yield config
                yield from audio

            # 执行识别
            responses_iterator = self.client.streaming_recognize(
                requests=requests(config_request, audio_requests)
            )

            current_text = ""
            for response in responses_iterator:
                for result in response.results:
                    if result.alternatives:
                        transcript = result.alternatives[0].transcript
                        is_final = result.is_final

                        # 更新当前文本
                        current_text = transcript

                        # 发送识别结果到WebSocket
                        msg = {'text': transcript, 'is_end': is_final}
                        await self.websocket.send_text(json.dumps(msg))

                        print(f"Google识别结果: {transcript}, 是否最终: {is_final}")

                        # 如果是最终结果，计算时长并扣除
                        if is_final and self.user:
                            # 假设每段音频约10秒
                            duration_seconds = 10
                            await DBService.deduct_audio_time(self.user.get("id"), duration_seconds)

            # 发送停止确认消息
            await self.websocket.send_json({
                'status': 'stopped',
                'message': 'Google ASR service stopped'
            })

        except Exception as e:
            print(f"Google处理缓冲音频错误: {str(e)}")
            traceback.print_exc()

            # 发送错误消息
            if self.websocket:
                await self.websocket.send_json({
                    'status': 'error',
                    'message': f'Google ASR error: {str(e)}'
                })


class SpeechRecognitionCallback(RecognitionCallback):
    def __init__(self, tag, websocket, loop, user) -> None:
        super().__init__()
        self.tag = tag
        self.text = ''
        self.websocket = websocket
        self.loop = loop
        self.send_events = []
        self.user = user

    def on_open(self) -> None:
        print(f'[{self.tag}] Recognition started')

    def on_complete(self) -> None:
        print(f'[{self.tag}] Results ==> ', self.text)
        print(f'[{self.tag}] Recognition completed')

    def on_error(self, result: RecognitionResult) -> None:
        print(f'[{self.tag}] RecognitionCallback task_id: ', result.request_id)
        print(f'[{self.tag}] RecognitionCallback error: ', result.message)

    async def send_asr_result(self, message: str,
                              event: asyncio.Event) -> None:
        await self.websocket.send_text(message)
        event.set()

    def on_event(self, result: RecognitionResult) -> None:
        try:
            sentence = result.get_sentence()
            if 'text' in sentence:
                is_end = False
                if RecognitionResult.is_sentence_end(sentence):
                    is_end = True
                    duration_seconds = sentence.get('end_time', 0) - sentence.get('begin_time', 0)
                    duration_seconds = duration_seconds / 1000 + 1
                    if duration_seconds > 0:
                        # 使用事件循环执行异步操作
                        asyncio.run_coroutine_threadsafe(
                            DBService.deduct_audio_time(self.user.get("id"), duration_seconds),
                            self.loop
                        )

                print(f"[{self.tag}] {sentence['text']}")
                msg = {'text': sentence['text'], 'is_end': is_end}
                event = asyncio.Event()
                self.send_events.append(event)
                self.loop.call_soon_threadsafe(
                    asyncio.create_task,
                    self.send_asr_result(json.dumps(msg), event))
        except Exception as e:
            print(f"处理事件错误: {str(e)}")
            traceback.print_exc()

    def on_close(self) -> None:
        print(f'[{self.tag}] RecognitionCallback closed')


# 语音识别服务工厂
class SpeechRecognitionFactory:
    @staticmethod
    def create_service(language):
        if language == "zh":
            return AliSpeechRecognitionService()
        else:  # 缅甸语或其他语言
            return GoogleSpeechRecognitionService()


@router.websocket("/ws/speech")
async def websocket_speech(websocket: WebSocket):
    """WebSocket端点处理语音识别请求"""
    await websocket.accept()
    print("WebSocket连接已接受")

    # 获取用户信息
    session = websocket.session
    user = session.get("user")
    print(f"用户信息: {user}")

    # 设置API密钥
    dashscope.api_key = "sk-196bc2b54b444440962781ef844e7720"

    recognition_service = None
    is_recognition_active = False

    try:
        while True:
            try:
                data = await websocket.receive()
            except RuntimeError as e:
                if "disconnect message has been received" in str(e):
                    print("WebSocket已断开连接")
                    break
                raise
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket连接已关闭")
                break

            if "text" in data:  # 文本消息
                message = data["text"]
                print(f"收到文本消息: {message}")

                # 处理停止信号
                if message == "stop":
                    print("收到停止信号")
                    if recognition_service and is_recognition_active:
                        await recognition_service.stop()
                        is_recognition_active = False

                        # 发送停止确认消息
                        await websocket.send_json({
                            'status': 'stopped',
                            'message': 'ASR service stopped'
                        })
                    return

                # 处理初始化请求
                try:
                    # 如果已有识别实例正在运行，先停止它
                    if recognition_service and is_recognition_active:
                        await recognition_service.stop()
                        is_recognition_active = False

                    # 解析配置
                    message_data = json.loads(message)
                    language = message_data.get("language", "zh")
                    print(f"设置语言为: {language}")

                    # 创建适当的识别服务
                    recognition_service = SpeechRecognitionFactory.create_service(language)

                    # 初始化识别服务
                    is_recognition_active = await recognition_service.initialize(websocket, user, language)

                    if is_recognition_active:
                        # 发送确认消息给客户端
                        await websocket.send_json({
                            'status': 'ready',
                            'message': '语音识别已准备就绪'
                        })
                    else:
                        await websocket.send_json({
                            'status': 'error',
                            'message': '语音识别初始化失败'
                        })
                except json.JSONDecodeError:
                    print(f"无法解析JSON: {message}")
                except Exception as e:
                    print(f"初始化识别错误: {str(e)}")
                    traceback.print_exc()
                    await websocket.send_json({
                        'status': 'error',
                        'message': f'初始化错误: {str(e)}'
                    })

            elif "bytes" in data and recognition_service and is_recognition_active:  # 二进制音频数据
                await recognition_service.process_audio(data["bytes"])
            elif "bytes" in data:
                print("警告: 收到音频数据但识别器未初始化或未激活")
                # 通知客户端需要重新初始化
                await websocket.send_json({
                    'status': 'error',
                    'message': '请重新开始录音'
                })

    except websockets.exceptions.ConnectionClosed:
        print("客户端断开连接")
    except Exception as e:
        print(f"WebSocket 错误: {str(e)}")
        traceback.print_exc()
    finally:
        # 确保关闭识别
        if recognition_service and is_recognition_active:
            try:
                print("关闭识别器")
                await recognition_service.stop()
            except Exception as e:
                print(f"关闭识别器错误: {str(e)}")
        print("关闭WebSocket连接")
        await websocket.close()
