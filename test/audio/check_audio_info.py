import os
from typing import Optional

def detect_audio_format(filename: str) -> Optional[str]:
    """通过文件头检测音频格式"""
    with open(filename, 'rb') as f:
        header = f.read(1024)  # 读取前1024字节分析

    # ---------- 格式检测逻辑（优先级从高到低） ----------
    # 1. WAV（RIFF头）
    if len(header) >= 12:
        if header[0:4] == b'RIFF' and header[8:12] == b'WAVE':
            return "WAV"

    # 2. FLAC（固定标识）
    if len(header) >= 4:
        if header[0:4] == b'fLaC':
            return "FLAC"

    # 3. OGG（固定头）
    if len(header) >= 4:
        if header[0:4] == b'OggS':
            return "OGG"

    # 4. MP3（ID3标签或MPEG帧头）
    # 检测ID3v2标签（文件头为"ID3"）
    if len(header) >= 10:
        if header[0:3] == b'ID3':
            return "MP3"
        # 检测MPEG帧头（0xFF Ex）
        if (header[0] == 0xFF) and ((header[1] & 0xE0) == 0xE0):
            return "MP3"

    # 5. MP4/M4A（ftyp原子）
    # 搜索头中的"ftyp"标识（可能偏移4字节）
    if len(header) >= 12:
        for i in range(0, min(len(header) - 8, 32), 4):  # 在前32字节内搜索
            if header[i:i+4] == b'ftyp':
                # 检查MP4品牌（如M4A、mp42、isom等）
                brand = header[i+4:i+8].decode('ascii', 'ignore')
                if brand in ['M4A ', 'mp42', 'isom']:
                    return "M4A/MP4"
                return "MP4"  # 通用MP4格式

    # 6. AAC-ADTS（ADTS同步字0xFFFx）
    if len(header) >= 2:
        if header[0] == 0xFF and (header[1] & 0xF0) == 0xF0:
            # 进一步检查ADTS头结构
            if (header[1] & 0x06) >> 1 == 0:  # MPEG-4标准
                return "AAC-ADTS"

    # 7. 其他格式尝试用mutagen探测
    try:
        from mutagen import File
        audio = File(filename)
        if audio is not None:
            return audio.__class__.__name__.upper()
    except ImportError:
        pass
    except Exception:
        pass

    return None  # 未知格式

# ---------- 示例用法 ----------
if __name__ == "__main__":
    files = [r"C:\Users\vsnot\Music\audio\a.bin"]
    for file in files:
        if not os.path.exists(file):
            print(f"文件 {file} 不存在")
            continue
        fmt = detect_audio_format(file)
        print(f"文件: {file} -> 格式: {fmt if fmt else '未知'}")

#
# # ---------- 示例用法 ----------
# if __name__ == "__main__":
#     # files = ["test.wav", "audio.m4a", "song.mp3", "stream.aac"]
#     files = [r"C:\Users\vsnot\Music\audio\a.bin"]
#     for file in files:
#         print(f"\n文件: {file}")
#         info = get_audio_info(file)
#         if "error" in info:
#             print(f"错误: {info['error']}")
#         else:
#             print(f"格式: {info['format']}")
#             print(f"时长: {info['duration']:.2f}秒")
#             print(f"采样率: {info['sample_rate']} Hz")
#             print(f"声道数: {info['channels']}")
#             print(f"比特率: {info['bitrate']} kbps" if info['bitrate'] else "比特率: N/A")