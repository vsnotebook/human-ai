from datetime import datetime, timedelta
from typing import Optional, Dict

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from src.core.config import settings

# MongoDB 连接
uri = "mongodb+srv://vswork666:VuSnbgmkrs4jamVt@cluster0.naywsqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.voice_workshop

class DemoMongoService:
    """试用功能相关的数据库操作"""
    
    @classmethod
    async def get_trial_record(cls, client_ip: str) -> Optional[Dict]:
        """获取IP的试用记录"""
        try:
            return db.trial_records.find_one({"ip": client_ip})
        except Exception as e:
            print(f"获取试用记录失败: {str(e)}")
            return None

    @classmethod
    async def create_or_update_trial_record(cls, client_ip: str, count: int) -> bool:
        """创建或更新试用记录"""
        try:
            current_time = datetime.utcnow()
            result = db.trial_records.update_one(
                {"ip": client_ip},
                {
                    "$set": {
                        "last_try": current_time,
                        "count": count
                    },
                    "$setOnInsert": {
                        "created_at": current_time,
                        "ip": client_ip
                    }
                },
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"更新试用记录失败: {str(e)}")
            return False

    @classmethod
    async def reset_trial_record(cls, client_ip: str) -> bool:
        """重置试用记录"""
        try:
            current_time = datetime.utcnow()
            result = db.trial_records.update_one(
                {"ip": client_ip},
                {
                    "$set": {
                        "count": 0,
                        "last_try": current_time,
                        "created_at": current_time
                    }
                },
                upsert=True
            )
            return result.modified_count > 0 or result.upserted_id is not None
        except Exception as e:
            print(f"重置试用记录失败: {str(e)}")
            return False

    @classmethod
    async def update_trial_count(cls, client_ip: str) -> Optional[Dict]:
        """更新试用次数并返回更新后的记录"""
        try:
            current_time = datetime.utcnow()
            trial_record = await cls.get_trial_record(client_ip)

            # 如果没有记录或记录已过期（14天），创建/重置记录
            if not trial_record or (current_time - trial_record["last_try"]) > timedelta(days=14):
                trial_record = {
                    "ip": client_ip,
                    "count": 0,
                    "last_try": current_time,
                    "created_at": current_time
                }

            # 更新试用次数
            new_count = trial_record["count"] + 1
            await cls.create_or_update_trial_record(client_ip, new_count)
            
            # 返回更新后的记录
            return await cls.get_trial_record(client_ip)
        except Exception as e:
            print(f"更新试用次数失败: {str(e)}")
            return None