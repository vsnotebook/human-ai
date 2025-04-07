from fastapi import APIRouter, WebSocket
from dashscope.audio.asr import Recognition, RecognitionCallback
import dashscope
import json
import asyncio

router = APIRouter()

class SpeechRecognitionCallback(RecognitionCallback):
    def __init__(self, websocket: WebSocket, language: str) -> None:
        super().__init__()
        self.websocket = websocket
        self.language = language
        self.text = ''

    async def on_message(self, message):
        try:
            if message.get('sentence'):
                sentence = message['sentence'][0]
                self.text = sentence['text']
                is_end = sentence.get('sentence_end', False)
                
                # 发送识别结果到客户端
                await self.websocket.send_json({
                    'text': self.text,
                    'is_end': is_end
                })
        except Exception as e:
            print(f"处理消息错误: {str(e)}")

@router.websocket("/ws/speech")
async def websocket_speech(websocket: WebSocket):
    await websocket.accept()
    
    try:
        # 初始化语音识别
        dashscope.api_key = "sk-196bc2b54b444440962781ef844e7720"
        
        while True:
            data = await websocket.receive()
            
            if "text" in data:  # 文本消息
                message = data["text"]
                if message == "stop":
                    # 处理停止录音的逻辑
                    continue
                    
                # 获取语言设置
                language = message.get("language", "zh")
                
                # 创建回调实例
                callback = SpeechRecognitionCallback(websocket, language)
                
                # 创建识别实例
                recognition = Recognition(
                    model='paraformer-realtime-v2',
                    format='wav',
                    sample_rate=16000,
                    language_hints=['zh', 'my', 'en'],
                    callback=callback
                )
                
            elif "bytes" in data:  # 二进制音频数据
                if recognition:
                    # 处理音频数据
                    await recognition.feed(data["bytes"])
            
    except Exception as e:
        print(f"WebSocket 错误: {str(e)}")
    finally:
        await websocket.close()