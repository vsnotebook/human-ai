import requests

def transcribe_audio(language,file_path):
    """
    将音频文件发送到 Cloudflare Worker 进行转写
    :param file_path: 音频文件路径
    :return: 转写结果
    """
    uri = 'https://asr.vswork666.workers.dev/'
    
    # 准备请求数据
    with open(file_path, 'rb') as audio_file:
        files = {'file': audio_file}
        data = {
            'model': 'whisper-1',
            'language': language
        }
        
        # 发送请求
        response = requests.post(uri, files=files, data=data)
        
        if response.ok:
            result = response.json()
            if result.get('vtt'):
                return result['text'].replace(' ', '，')
            else:
                return '无法取得字幕档案'
        else:
            return '语音转文字失败，请检查服务器设置'

if __name__ == '__main__':
    # 使用示例
    # audio_file_path = r'D:\vs-program\google\py\web-cloud\test\google\asr\resources\让我来告诉你吧——是手心啊，哈哈哈.wav'
    # audio_file_path = r'..\google\asr\resources\让我来告诉你吧——是手心啊，哈哈哈.wav'
    # audio_file_path = r'..\google\asr\resources\多人对话-中文.wav'
    # audio_file_path = r'..\google\asr\resources\历代名人咏江阴_耳聆网.mp3'
    audio_file_path_zh = r'..\google\asr\resources\徐秀娟故居讲解词.mp3'
    audio_file_path_my = r'..\google\asr\resources\用户发送了一段中文文本，并希望将其翻译成缅甸文-缅甸语.mp3'
    # result_zh = transcribe_audio('zh',audio_file_path_zh)
    # print(f"转写结果：{result_zh}")
    result_my = transcribe_audio('my',audio_file_path_my)
    print(f"转写结果：{result_my}")