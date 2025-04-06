from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="zh-Hant">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>语音转文字</title>
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/water.css@2/out/dark.css">
    </head>
    <body>
        <h1>语音转文字</h1>
        <form action="/transcribe" method="post" enctype="multipart/form-data">
            <input type="file" name="file" accept="audio/*,video/*" required>
            <button type="submit">上传并转换</button>
        </form>
        <div class="output-section">
            <h2>识别结果</h2>
            <pre id="originalOutput">{{ result }}</pre>
        </div>
    </body>
    </html>
    '''

@app.route('/transcribe', methods=['POST'])
def transcribe():
    if 'file' not in request.files:
        return jsonify({'error': '请选择一个音频文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400

    # 准备发送到Cloudflare Worker的请求
    uri = 'https://asr.vswork666.workers.dev/'
    files = {'file': (file.filename, file.stream)}
    data = {
        'model': 'whisper-1',
        'language': 'myanmar'
    }

    try:
        response = requests.post(uri, files=files, data=data)
        if response.ok:
            result = response.json()
            if result.get('vtt'):
                text = result['text'].replace(' ', '，')
                return jsonify({'text': text})
            else:
                return jsonify({'error': '无法取得字幕档案'}), 400
        else:
            return jsonify({'error': '语音转文字失败，请检查服务器设置'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)