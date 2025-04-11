import os
import tkinter as tk
from tkinter import filedialog, ttk
import azure.cognitiveservices.speech as speechsdk
from datetime import datetime

# 配置Azure语音服务的密钥和区域
speech_key=os.environ.get('SPEECH_KEY')
service_region=os.environ.get('SPEECH_REGION')
# speech_key = "key"
# service_region = "service_region"


def recognize_speech():
    # 获取选择的WAV文件路径
    wav_file = filedialog.askopenfilename(filetypes=[("WAV Files", "*.wav")])

    if wav_file:
        # 更新状态标签
        status_label.config(text="正在识别...")

        # 创建语音配置对象,并设置语言为中文
        speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
        speech_config.speech_recognition_language = "zh-CN"

        # 创建音频配置对象
        audio_config = speechsdk.audio.AudioConfig(filename=wav_file)

        # 创建语音识别器对象
        speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

        # 定义识别结果的回调函数
        recognized_text = []

        def handle_final_result(evt):
            recognized_text.append(evt.result.text)
            progress_bar.step(10)  # 每次识别结果更新进度条

        # 连接识别结果的事件处理程序
        speech_recognizer.recognized.connect(handle_final_result)

        # 定义识别状态的标志变量
        is_recognizing = True

        # 定义识别结束的回调函数
        def handle_session_stopped(evt):
            nonlocal is_recognizing
            is_recognizing = False

        # 连接识别结束的事件处理程序
        speech_recognizer.session_stopped.connect(handle_session_stopped)

        # 执行连续识别
        speech_recognizer.start_continuous_recognition()

        # 等待连续识别完成
        while is_recognizing:
            window.update()

        # 停止连续识别
        speech_recognizer.stop_continuous_recognition()

        # 获取当前时间戳
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # 构建保存文件的路径
        save_path = os.path.join("./", f"recognized_text_{timestamp}.txt")

        # 将识别结果保存到文件
        with open(save_path, "w", encoding="utf-8") as file:
            file.write("\n".join(recognized_text))

        # 更新状态标签
        status_label.config(text="识别完成,结果已保存到文件: " + save_path)

        # 重置进度条
        progress_bar["value"] = 0


# 创建图形化界面
window = tk.Tk()
window.title("语音识别")

# 创建选择文件按钮
select_button = tk.Button(window, text="选择WAV文件", command=recognize_speech)
select_button.pack(pady=10)

# 创建状态标签
status_label = tk.Label(window, text="请选择要识别的WAV文件")
status_label.pack()

# 创建进度条
progress_bar = ttk.Progressbar(window, length=200, mode="determinate")
progress_bar.pack(pady=10)

# 运行图形化界面
window.mainloop()