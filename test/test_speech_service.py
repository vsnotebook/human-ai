import asyncio
import os
os.chdir('../')



from src.services.speech_service import SpeechService


async def test_transcribe():
    # 读取音频文件
    audio_file_path = r"C:\Users\vsnot\Music\audio\让我来告诉你吧——是手心啊，哈哈哈.wav"
    with open(audio_file_path, "rb") as audio_file:
        audio_content = audio_file.read()

    # 调用 transcribe 函数，使用中文配置
    result = await SpeechService.transcribe(audio_content, "zh-CN")
    
    # 打印识别结果
    print("\n转录结果:", result)
    
    # 基本验证
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0

# 运行测试
if __name__ == "__main__":
    asyncio.run(test_transcribe())