from http import HTTPStatus
from dashscope.audio.asr import Recognition

# pip install -U dashscope
# 若没有将API Key配置到环境变量中，需将下面这行代码注释放开，并将apiKey替换为自己的API Key
import dashscope
dashscope.api_key = "sk-196bc2b54b444440962781ef844e7720"

recognition = Recognition(model='paraformer-realtime-v2',
                          format='wav',
                          sample_rate=48000,
                          # “language_hints”只支持paraformer-realtime-v2模型
                          language_hints=['zh', 'en'],
                          callback=None)
# result = recognition.call('../../resources/asr_example.wav')
result = recognition.call(r'C:\Users\vsnot\AppData\Local\Temp\tmp0fxv720d.wav')
if result.status_code == HTTPStatus.OK:
    print('识别结果：')
    print(result.get_sentence())
else:
    print('Error: ', result.message)

print(
    '[Metric] requestId: {}, first package delay ms: {}, last package delay ms: {}'
    .format(
        recognition.get_last_request_id(),
        recognition.get_first_package_delay(),
        recognition.get_last_package_delay(),
    ))


