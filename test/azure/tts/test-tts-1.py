import os

from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
from azure.cognitiveservices.speech.audio import AudioOutputConfig
from azure.cognitiveservices.speech import ResultReason, CancellationReason

subscription=os.environ.get('SPEECH_KEY')
region=os.environ.get('SPEECH_REGION')

# 创建SpeechConfig对象
speech_config = SpeechConfig(subscription=subscription, region=region)

# 创建音频配置对象
audio_config = AudioConfig(filename="output.mp3")  # 输出到MP3文件

# 创建语音合成器
speech_synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
text = "How To Unlock Cyberpunk 2077’s New Ending In Phantom Liberty"

# 定义SSML文本


ssml_string2 = """
<!--ID=B7267351-473F-409D-9765-754A8EBCDE05;Version=1|{"VoiceNameToIdMapItems":[{"Id":"390baec9-d867-4c01-bdcf-04e5848ee7dc","Name":"Microsoft Server Speech Text to Speech Voice (zh-CN, XiaoxiaoMultilingualNeural)","ShortName":"zh-CN-XiaoxiaoMultilingualNeural","Locale":"zh-CN","VoiceType":"StandardVoice"}]}-->
<!--ID=FCB40C2B-1F9F-4C26-B1A1-CF8E67BE07D1;Version=1|{"Files":{}}-->
<!--ID=5B95B1CC-2C7B-494F-B746-CF22A0E779B7;Version=1|{"Locales":{"zh-CN":{"AutoApplyCustomLexiconFiles":[{}]},"de-DE":{"AutoApplyCustomLexiconFiles":[{}]}}}-->
<speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" xmlns:emo="http://www.w3.org/2009/10/emotionml" version="1.0" xml:lang="zh-CN"><voice name="zh-CN-XiaoxiaoMultilingualNeural"><lang xml:lang="zh-CN"><s />但我现在对这个职业的热爱还是非常的，呵呵,非常的，嗯,怎么说呢？日月可鉴的，哈哈，嗯还是希望可以把这个职业做下去或者做这个声音相关领域的工作，嗯，就是把自己的优势发挥的大一点，尽可能能用到自己擅长的东西，而不是说为了工作，为了挣钱而工作。<s /></lang></voice></speak>
"""

# 使用SSML文本进行语音合成
result = speech_synthesizer.speak_ssml_async(ssml_string2).get()

# 检查结果
if result.reason == ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized to [output.mp3] for text [{}]".format(ssml_string2))
elif result.reason == ResultReason.Canceled:
    cancellation_details = result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
    print("Did you update the subscription info?")