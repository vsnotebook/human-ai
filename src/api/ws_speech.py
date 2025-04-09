import traceback
import json
import os
import asyncio

import dashscope
import websockets
from fastapi import APIRouter, WebSocket
from dashscope.audio.asr import Recognition, RecognitionCallback, RecognitionResult
from src.services.firestore_service import FirestoreService as DBService

router = APIRouter()

# 实时语音识别回调类，参考自server.py中的MyRecognitionCallback
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
                    duration_seconds = duration_seconds/1000+1
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

@router.websocket("/ws/speech")
async def websocket_speech(websocket: WebSocket):
    await websocket.accept()
    print("WebSocket连接已接受")

    # 获取用户ID
    session = websocket.session
    user = session.get("user")
    print(f"用户ID: {user}")

    dashscope.api_key = "sk-196bc2b54b444440962781ef844e7720"

    recognition = None
    is_recognition_active = False
    callback = None
    
    try:
        # 初始化语音识别
        while True:
            data = await websocket.receive()
            # print("http_proxy: " + os.getenv("http_proxy"))
            if "text" in data:  # 文本消息
                message = data["text"]
                print(f"收到文本消息: {message}")
                
                # 检查是否为停止信号
                if message == "stop":
                    print("收到停止信号，停止识别")
                    if recognition and is_recognition_active:
                        try:
                            recognition.stop()
                            is_recognition_active = False
                            
                            # 等待所有ASR结果发送完成
                            if callback:
                                for event in callback.send_events:
                                    await event.wait()
                            
                            # 将字符串消息改为JSON格式
                            await websocket.send_json({
                                'status': 'stopped',
                                'message': 'ASR service stopped'
                            })
                            print('asr stopped')
                        except Exception as e:
                            print(f"停止识别错误: {str(e)}")
                    continue
                
                try:
                    # 如果已有识别实例正在运行，先停止它
                    if recognition and is_recognition_active:
                        try:
                            recognition.stop()
                            is_recognition_active = False
                        except Exception as e:
                            print(f"停止旧识别实例错误: {str(e)}")
                    
                    # 尝试解析JSON字符串
                    message_data = json.loads(message)
                    
                    # 获取语言设置
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
                    is_recognition_active = True
                    print("语音识别已启动")
                    
                    # 发送确认消息给客户端
                    await websocket.send_json({
                        'status': 'ready',
                        'message': '语音识别已准备就绪'
                    })
                    
                except json.JSONDecodeError:
                    print(f"无法解析JSON: {message}")
                except Exception as e:
                    print(f"初始化识别错误: {str(e)}")
                    traceback.print_exc()
                    
            elif "bytes" in data:  # 二进制音频数据
                if recognition and is_recognition_active:
                    try:
                        # 处理音频数据
                        audio_data = data["bytes"]
                        audio_len = len(audio_data)
                        print(f"收到音频数据: {audio_len} 字节")
                        recognition.send_audio_frame(audio_data)
                    except Exception as e:
                        print(f"发送音频数据错误: {str(e)}")
                        traceback.print_exc()
                else:
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