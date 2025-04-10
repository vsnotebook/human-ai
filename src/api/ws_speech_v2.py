import asyncio
import json
import traceback

import dashscope
import websockets
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
from fastapi import APIRouter, WebSocket

from src.services.firestore_service import FirestoreService as DBService

router = APIRouter()


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
                        # TODO
                        #                         result = await DBService.deduct_audio_time(self.user_id, duration_seconds)
                        #                         if result:
                        #                             print(f"成功扣除试用时长: {duration_seconds}秒")
                        #                         else:
                        #                             print("扣除试用时长失败")

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


async def stop_recognition(recognition, callback, websocket):
    """停止语音识别并通知客户端"""
    try:
        recognition.stop()
        
        # 等待所有ASR结果发送完成
        if callback:
            for event in callback.send_events:
                await event.wait()
        
        # 发送停止确认消息
        await websocket.send_json({
            'status': 'stopped',
            'message': 'ASR service stopped'
        })
        print('ASR service stopped')
        return True
    except Exception as e:
        print(f"停止识别错误: {str(e)}")
        return False


async def initialize_recognition(message, websocket, user):
    """初始化语音识别服务"""
    try:
        # 解析配置
        message_data = json.loads(message)
        language = message_data.get("language", "zh")
        print(f"设置语言为: {language}")
        
        # 创建回调实例
        loop = asyncio.get_event_loop()
        callback = SpeechRecognitionCallback('process0', websocket, loop, user)
        
        # 创建识别实例
        recognition = Recognition(
            model='paraformer-realtime-v2',
            format='pcm',
            sample_rate=16000,
            language_hints=['zh', 'my', 'en'] if language == 'zh' else ['my', 'zh', 'en'],
            semantic_punctuation_enabled=False,
            callback=callback
        )
        
        # 启动识别
        recognition.start()
        print("语音识别已启动")
        
        # 发送确认消息给客户端
        await websocket.send_json({
            'status': 'ready',
            'message': '语音识别已准备就绪'
        })
        
        return recognition, callback, True
    except json.JSONDecodeError:
        print(f"无法解析JSON: {message}")
        return None, None, False
    except Exception as e:
        print(f"初始化识别错误: {str(e)}")
        traceback.print_exc()
        return None, None, False


async def process_audio_data(recognition, audio_data, websocket):
    """处理接收到的音频数据"""
    try:
        audio_len = len(audio_data)
        print(f"收到音频数据: {audio_len} 字节")
        recognition.send_audio_frame(audio_data)
        return True
    except Exception as e:
        print(f"发送音频数据错误: {str(e)}")
        traceback.print_exc()
        return False


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

    recognition = None
    is_recognition_active = False
    callback = None

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
                    if recognition and is_recognition_active:
                        is_recognition_active = not await stop_recognition(recognition, callback, websocket)
                    return

                # 处理初始化请求
                # 如果已有识别实例正在运行，先停止它
                if recognition and is_recognition_active:
                    try:
                        recognition.stop()
                        is_recognition_active = False
                    except Exception as e:
                        print(f"停止旧识别实例错误: {str(e)}")

                # 初始化新的识别实例
                recognition, callback, is_recognition_active = await initialize_recognition(
                    message, websocket, user
                )

            elif "bytes" in data and recognition and is_recognition_active:  # 二进制音频数据
                await process_audio_data(recognition, data["bytes"], websocket)
            elif "bytes" in data:
                print("警告: 收到音频数据但识别器未初始化或未激活")
                # 通知客户端需要重新初始化
                if False:
                    await websocket.send_json({
                        'status': 'error',
                        'message': '请重新开始录音'
                    })
                pass

    except websockets.exceptions.ConnectionClosed:
        print("客户端断开连接")
    except Exception as e:
        print(f"WebSocket 错误: {str(e)}")
        traceback.print_exc()
    finally:
        # 确保关闭识别
        if recognition and is_recognition_active:
            try:
                print("关闭识别器")
                recognition.stop()
            except Exception as e:
                print(f"关闭识别器错误: {str(e)}")
        print("关闭WebSocket连接")
        await websocket.close()
