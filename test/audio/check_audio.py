import os
import wave
from mutagen import File as MutagenFile
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.aac import AAC
import struct


def analyze_audio_file(file_path: str) -> dict:
    """分析音频文件信息"""
    result = {
        "文件名": os.path.basename(file_path),
        "文件大小": f"{os.path.getsize(file_path) / 1024:.2f} KB",
        "格式": "未知",
        "时长": None,
        "采样率": None,
        "比特率": None,
        "声道数": None,
        "编码格式": None
    }

    # 读取文件头
    with open(file_path, 'rb') as f:
        header = f.read(32)

    # 通过文件头特征识别格式
    if header.startswith(b'RIFF') and b'WAVE' in header[:12]:
        result["格式"] = "WAV"
        try:
            with wave.open(file_path, 'rb') as wav:
                result["采样率"] = wav.getframerate()
                result["声道数"] = wav.getnchannels()
                result["时长"] = wav.getnframes() / float(wav.getframerate())
                result["比特率"] = wav.getsampwidth() * 8 * wav.getframerate() * wav.getnchannels()
                result["编码格式"] = wav.getcomptype()
        except Exception as e:
            result["错误"] = f"WAV解析失败: {str(e)}"

    # AAC-ADTS格式检查
    elif header.startswith(b'\xff\xf1') or header.startswith(b'\xff\xf9'):
        result["格式"] = "AAC-ADTS"
        try:
            audio = AAC(file_path)
            result.update({
                "时长": audio.info.length,
                "采样率": audio.info.sample_rate,
                "声道数": audio.info.channels,
                "比特率": audio.info.bitrate
            })
        except Exception as e:
            result["错误"] = f"AAC解析失败: {str(e)}"

    # MP4/M4A格式检查 (ftyp标记)
    elif b'ftyp' in header[4:8]:
        result["格式"] = "M4A/MP4"
        try:
            audio = MP4(file_path)
            result.update({
                "时长": audio.info.length,
                "采样率": audio.info.sample_rate,
                "声道数": audio.info.channels,
                "比特率": audio.info.bitrate
            })
        except Exception as e:
            result["错误"] = f"M4A/MP4解析失败: {str(e)}"

    # MP3格式检查 (ID3或同步标记)
    elif header.startswith(b'ID3') or header.startswith(b'\xff\xfb') or header.startswith(
            b'\xff\xf3') or header.startswith(b'\xff\xf2'):
        result["格式"] = "MP3"
        try:
            audio = MP3(file_path)
            result.update({
                "时长": audio.info.length,
                "采样率": audio.info.sample_rate,
                "比特率": audio.info.bitrate,
                "声道数": 1 if audio.info.mode == 3 else 2
            })
        except Exception as e:
            result["错误"] = f"MP3解析失败: {str(e)}"

    # 如果上述格式都不匹配，尝试使用通用mutagen解析
    else:
        try:
            audio = MutagenFile(file_path)
            if audio is not None and hasattr(audio, 'info'):
                result["格式"] = type(audio).__name__
                if hasattr(audio.info, 'length'):
                    result["时长"] = audio.info.length
                if hasattr(audio.info, 'sample_rate'):
                    result["采样率"] = audio.info.sample_rate
                if hasattr(audio.info, 'channels'):
                    result["声道数"] = audio.info.channels
                if hasattr(audio.info, 'bitrate'):
                    result["比特率"] = audio.info.bitrate
        except Exception as e:
            result["错误"] = f"音频格式无法识别: {str(e)}"

    # 格式化输出
    if result["时长"] is not None:
        result["时长"] = f"{result['时长']:.2f} 秒"
    if result["比特率"] is not None:
        result["比特率"] = f"{result['比特率'] / 1000:.0f} kbps"
    if result["采样率"] is not None:
        result["采样率"] = f"{result['采样率']} Hz"

    return result


def print_audio_info(file_path: str):
    """打印音频文件信息"""
    info = analyze_audio_file(file_path)
    print("\n=== 音频文件信息 ===")
    for key, value in info.items():
        if value is not None:
            print(f"{key}: {value}")


# ffmpeg -i "input.aac" -acodec pcm_s16le -ar 16000 -ac 1 "output.wav"
# ffmpeg -i "a.mp3" -acodec pcm_s16le -ar 16000 -ac 1 "output.wav"

if __name__ == "__main__":
    # 示例用法
    # print_audio_info(r"C:\Users\vsnot\Music\audio\a.bin")
    # print_audio_info(r"D:\vs-program\google\py\web-cloud\debug_audio\audio_debug_20250402_233347.bin")
    # print_audio_info(r"D:\vs-program\google\py\web-cloud\debug_audio\audio_debug_20250402_224021.m4a")
    print_audio_info(r"D:\vs-program\google\py\web-cloud\test\google\asr\resources\第五十六条 经营者违反本法规定，达成并实施垄断协议的，由反垄断执法机构责令停止违法行为，没收违法所得，并处上一年度销售额百分之一以上百分之十以下的罚款.mp3")
