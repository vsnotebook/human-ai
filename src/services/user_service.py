from typing import Dict, Any
import datetime
import tempfile
import os
import wave

from bson import ObjectId
from mutagen import File as MutagenFile
from src.db.mongodb import db

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
        # 从 user_balance 表获取用户余额信息
        balance_collection = db.user_balance
        
        # 获取用户当前余额信息
        balance = balance_collection.find_one({'user_id': user_id})
        if not balance:
            # 如果没有余额记录，创建一个新的
            balance = {
                "user_id": user_id,
                "asr_balance": 60,  # 默认1分钟
                "tts_balance": 500,
                "text_translation_balance": 0,
                "voice_translation_balance": 0,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
            balance_collection.insert_one(balance)
        
        # 计算剩余时长
        remaining_seconds = balance.get("asr_balance", 0)
        if remaining_seconds < audio_duration_seconds:
            raise ValueError("语音识别时长余额不足")
        
        # 扣除时长
        new_remaining_seconds = remaining_seconds - audio_duration_seconds
        
        # 更新用户余额信息
        update_result = balance_collection.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "asr_balance": new_remaining_seconds,
                    "updated_at": datetime.datetime.utcnow()
                },
                "$inc": {
                    "total_asr_usage_seconds": audio_duration_seconds
                }
            }
        )
        
        if update_result.modified_count == 0:
            raise ValueError("更新用户余额失败")
        
        # 返回更新后的用户余额信息
        updated_balance = balance_collection.find_one({"user_id": user_id})
        return updated_balance
    
    @staticmethod
    async def get_audio_duration(audio_content: bytes) -> int:
        """
        获取音频文件的时长（秒），使用不依赖ffmpeg的库
        
        Args:
            audio_content: 音频文件内容
            
        Returns:
            音频时长（秒）
        """
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