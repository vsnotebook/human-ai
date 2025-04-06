from openai import OpenAI

client = OpenAI()

audio_file_path_zh = r'..\google\asr\resources\让我来告诉你吧——是手心啊，哈哈哈.wav'
# audio_file_path_my = r'..\google\asr\resources\用户发送了一段中文文本，并希望将其翻译成缅甸文-缅甸语.mp3'
audio_file= open(audio_file_path_zh, "rb")

transcription = client.audio.transcriptions.create(
    model="gpt-4o-transcribe",
    file=audio_file
)

print(transcription.text)