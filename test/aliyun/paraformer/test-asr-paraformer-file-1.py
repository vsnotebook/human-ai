import json
from http import HTTPStatus

import requests
from dashscope.audio.asr import Transcription

# 若没有将API Key配置到环境变量中，需将下面这行代码注释放开，并将apiKey替换为自己的API Key
# import dashscope
# dashscope.api_key = "apiKey"

task_response = Transcription.async_call(
    model='paraformer-v2',
    file_urls=[
        # 'https://dashscope.oss-cn-beijing.aliyuncs.com/samples/audio/paraformer/hello_world_female2.wav',
        # 'https://vsaudio2.oss-cn-heyuan.aliyuncs.com/%E5%A4%9A%E4%BA%BA%E5%AF%B9%E8%AF%9D-%E4%B8%AD%E6%96%87.wav'],
        'https://vsaudio2.oss-cn-heyuan.aliyuncs.com/%E5%BE%90%E7%A7%80%E5%A8%9F%E6%95%85%E5%B1%85%E8%AE%B2%E8%A7%A3%E8%AF%8D.mp3'],
    language_hints=['zh', 'en']  # “language_hints”只支持paraformer-v2模型
)

transcribe_response = Transcription.wait(task=task_response.output.task_id)
if transcribe_response.status_code == HTTPStatus.OK:
    print(json.dumps(transcribe_response.output, indent=4, ensure_ascii=False))
    print('transcription done!')

    # 获取识别结果
    if transcribe_response.output.results:
        transcription_url = transcribe_response.output.results[0]['transcription_url']
        try:
            # 获取转写结果
            result_response = requests.get(transcription_url)
            if result_response.status_code == 200:
                result_content = result_response.json()
                print("\n识别内容：")
                print(json.dumps(result_content, indent=4, ensure_ascii=False))
            else:
                print(f"获取识别结果失败，状态码：{result_response.status_code}")
        except Exception as e:
            print(f"获取识别结果时发生错误：{str(e)}")

    print('transcription done!')
