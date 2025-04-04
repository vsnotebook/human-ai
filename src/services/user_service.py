from typing import Dict, Any
import datetime
import tempfile
import os
import wave
from mutagen import File as MutagenFile
from src.services.mongodb_service import MongoDBService as DBService

class UserService:
    @staticmethod
    async def deduct_audio_time(user_id: str, audio_duration_seconds: int) -> Dict[str, Any]:
        """
        扣除用户的语音识别时长余额
        
        Args:
            user_id: 用户ID
            audio_duration_seconds: 音频时长（秒）
            
        Returns:
            更新后的用户信息
        """
        ret = await DBService.deduct_audio_time(user_id, audio_duration_seconds)
        print(ret)
        return ret
    
    @staticmethod
    async def get_audio_duration(audio_content: bytes) -> int:
        """
        获取音频文件的时长（秒），使用不依赖ffmpeg的库
        
        Args:
            audio_content: 音频文件内容
            
        Returns:
            音频时长（秒）
        """
        ######################################################################################################
        # # 保存上传的音频文件到本地，用于检查格式
        # debug_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "debug_audio")
        # os.makedirs(debug_dir, exist_ok=True)
        # # debug_file_path = os.path.join(debug_dir, f"audio_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bin")
        # debug_file_path = os.path.join(debug_dir, f"audio_debug_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.bin")
        # with open(debug_file_path, 'wb') as f:
        #     f.write(audio_content)
        # print(f"已保存音频文件到: {debug_file_path}")
        ######################################################################################################

        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_content)
            temp_file_path = temp_file.name
        
        try:
            # 首先尝试使用wave库（适用于WAV格式）
            try:
                with wave.open(temp_file_path, 'rb') as wav_file:
                    frames = wav_file.getnframes()
                    rate = wav_file.getframerate()
                    duration = frames / float(rate)
                    return int(duration) + 1  # 向上取整，确保至少为1秒
            except:
                # 如果不是WAV格式，尝试使用mutagen
                audio = MutagenFile(temp_file_path)
                if audio is not None and hasattr(audio, 'info') and hasattr(audio.info, 'length'):
                    return int(audio.info.length) + 1  # 向上取整
                else:
                    # 如果无法解析，返回默认值
                    print("无法使用mutagen获取音频时长")
                    return 60  # 默认60秒
        except Exception as e:
            # 如果无法解析，返回默认值
            print(f"无法获取音频时长: {str(e)}")
            return 60  # 默认60秒
        finally:
            # 删除临时文件
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)