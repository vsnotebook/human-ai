import time

from fastapi import APIRouter, File, UploadFile, Form, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
import azure.cognitiveservices.speech as speechsdk
import os
import tempfile
import uuid
import asyncio
import base64
import io

# 创建路由器
router = APIRouter()

# 设置Azure语音服务的密钥和区域
speech_key = os.environ.get('SPEECH_KEY')
speech_endpoint = "https://southeastasia.api.cognitive.microsoft.com/"

@router.post("/transcribe_once")
async def transcribe_audio(audio_file: UploadFile = File(...), language: str = Form(...)):
    """
    接收音频文件并使用Azure语音识别服务进行转录
    支持的语言: zh-CN (中文), my-MM (缅甸文)
    """
    # 检查语言是否支持
    if language not in ["zh-CN", "my-MM"]:
        return JSONResponse(
            status_code=400,
            content={"error": "不支持的语言。请使用 zh-CN (中文) 或 my-MM (缅甸文)"}
        )
    
    # 保存上传的音频文件到临时目录
    temp_file_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.wav"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await audio_file.read())
    
    try:
        # 配置语音识别
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
        speech_config.speech_recognition_language = language
        
        # 配置音频输入
        audio_config = speechsdk.audio.AudioConfig(filename=temp_file_path)
        
        # 创建语音识别器
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # 执行语音识别
        # result = speech_recognizer.recognize_once()
        result = speech_recognizer.recognize_once_async().get()

        # 处理结果
        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            return {"text": result.text, "language": language}
        elif result.reason == speechsdk.ResultReason.NoMatch:
            return {"error": "无法识别语音", "details": str(result.no_match_details)}
        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason))
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details))
            print(result.cancellation_details.error_details)
            return {"error": f"语音识别已取消: {cancellation_details.reason}", 
                    "details": cancellation_details.error_details if cancellation_details.reason == speechsdk.CancellationReason.Error else ""}
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"处理音频时出错: {str(e)}"}
        )
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            # os.remove(temp_file_path)
            pass


@router.post("/transcribe_continuous")
async def transcribe_audio_continuous(audio_file: UploadFile = File(...), language: str = Form(...)):
    """
    接收音频文件并使用Azure语音识别服务进行连续转录（识别多句话）
    支持的语言: zh-CN (中文), my-MM (缅甸文)
    """
    # 检查语言是否支持
    if language not in ["zh-CN", "my-MM"]:
        return JSONResponse(
            status_code=400,
            content={"error": "不支持的语言。请使用 zh-CN (中文) 或 my-MM (缅甸文)"}
        )
    
    # 保存上传的音频文件到临时目录
    temp_file_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}.wav"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await audio_file.read())
    
    try:
        # 配置语音识别
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
        speech_config.speech_recognition_language = language
        
        # 配置音频输入
        audio_config = speechsdk.audio.AudioConfig(filename=temp_file_path)
        
        # 创建语音识别器
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # 存储识别结果
        all_results = []
        done = False
        start_time = time.time()
        last_result_time = start_time
        
        # 定义回调函数
        def recognized_cb(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                all_results.append(evt.result.text)
                nonlocal last_result_time
                last_result_time = time.time()
        
        def stop_cb(evt):
            nonlocal done
            done = True
        
        # 连接回调函数到事件
        speech_recognizer.recognized.connect(recognized_cb)
        speech_recognizer.session_stopped.connect(stop_cb)
        speech_recognizer.canceled.connect(stop_cb)
        
        # 开始连续语音识别
        speech_recognizer.start_continuous_recognition()
        
        # 等待识别完成
        max_wait_time = 30  # 最大等待时间（秒）
        while not done and (time.time() - start_time) < max_wait_time:
            time.sleep(0.5)
            
            # 如果5秒内没有新的识别结果，且已有结果，认为识别已完成
            if len(all_results) > 0 and (time.time() - last_result_time) > 5:
                done = True
        
        # 停止识别
        speech_recognizer.stop_continuous_recognition()
        
        # 返回所有识别结果
        return {
            "text": " ".join(all_results),
            "sentences": all_results,
            "language": language
        }
        
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"处理音频时出错: {str(e)}"}
        )
    finally:
        # 清理临时文件
        if os.path.exists(temp_file_path):
            # os.remove(temp_file_path)
            pass


@router.websocket("/realtime_transcribe")
async def realtime_transcribe(websocket: WebSocket):
    """
    通过WebSocket接收实时音频流并使用Azure语音识别服务进行实时转录
    """
    await websocket.accept()
    
    try:
        # 获取初始配置
        config_data = await websocket.receive_json()
        language = config_data.get("language", "zh-CN")
        
        # 检查语言是否支持
        if language not in ["zh-CN", "my-MM"]:
            await websocket.send_json({
                "error": "不支持的语言。请使用 zh-CN (中文) 或 my-MM (缅甸文)"
            })
            await websocket.close()
            return
        
        # 配置语音识别
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, endpoint=speech_endpoint)
        speech_config.speech_recognition_language = language
        
        # 创建推送流
        push_stream = speechsdk.audio.PushAudioInputStream()
        audio_config = speechsdk.audio.AudioConfig(stream=push_stream)
        
        # 创建语音识别器
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
        
        # 创建一个队列用于存储识别结果
        result_queue = asyncio.Queue()
        
        # 设置回调函数
        def on_recognized(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizedSpeech:
                print(evt.result.text)
                result_queue.put_nowait({"type": "final", "text": evt.result.text})
        
        def on_recognizing(evt):
            if evt.result.reason == speechsdk.ResultReason.RecognizingSpeech:
                print(evt.result.text)
                result_queue.put_nowait({"type": "interim", "text": evt.result.text})
        
        # 连接回调函数
        speech_recognizer.recognized.connect(on_recognized)
        speech_recognizer.recognizing.connect(on_recognizing)
        
        # 开始连续语音识别
        speech_recognizer.start_continuous_recognition()
        
        # 创建一个任务来处理结果队列
        async def process_results():
            while True:
                try:
                    result = await result_queue.get()
                    await websocket.send_json(result)
                    result_queue.task_done()
                except Exception as e:
                    print(f"处理结果时出错: {str(e)}")
                    break
        
        # 启动结果处理任务
        result_processor = asyncio.create_task(process_results())
        
        # 持续接收音频数据
        while True:
            try:
                data = await websocket.receive_text()
                
                # 检查是否是控制命令
                if data == "STOP":
                    break
                
                # 解码Base64音频数据
                audio_data = base64.b64decode(data.split(",")[1] if "," in data else data)
                
                # 推送到流
                push_stream.write(audio_data)
                
            except WebSocketDisconnect:
                break
            except Exception as e:
                await websocket.send_json({"error": f"处理音频时出错: {str(e)}"})
                break
        
        # 取消结果处理任务
        result_processor.cancel()
        try:
            await result_processor
        except asyncio.CancelledError:
            pass
        
        # 停止识别
        speech_recognizer.stop_continuous_recognition()
        push_stream.close()
        
    except Exception as e:
        try:
            await websocket.send_json({"error": f"服务器错误: {str(e)}"})
        except:
            pass
    finally:
        try:
            await websocket.close()
        except:
            pass
