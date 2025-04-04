from datetime import datetime, timedelta
from typing import Optional, Dict

from google.cloud import firestore
from google.cloud.firestore import Client

from src.core.config import settings

# Firestore 连接
db: Client = firestore.Client(project=settings.PROJECT_ID)

class DemoFirestoreService:
    """试用功能相关的数据库操作"""
    
    @classmethod
    async def get_trial_record(cls, client_ip: str) -> Optional[Dict]:
        """获取IP的试用记录"""
        try:
            doc_ref = db.collection('trial_records').document(client_ip)
            doc = doc_ref.get()
            return doc.to_dict() if doc.exists else None
        except Exception as e:
            print(f"获取试用记录失败: {str(e)}")
            return None

    @classmethod
    async def create_or_update_trial_record(cls, client_ip: str, count: int) -> bool:
        """创建或更新试用记录"""
        try:
            current_time = datetime.utcnow()
            doc_ref = db.collection('trial_records').document(client_ip)
            
            # 获取现有记录
            doc = doc_ref.get()
            if doc.exists:
                # 更新现有记录
                doc_ref.update({
                    "last_try": current_time,
                    "count": count
                })
            else:
                # 创建新记录
                doc_ref.set({
                    "ip": client_ip,
                    "last_try": current_time,
                    "count": count,
                    "created_at": current_time
                })
            return True
        except Exception as e:
            print(f"更新试用记录失败: {str(e)}")
            return False

    @classmethod
    async def reset_trial_record(cls, client_ip: str) -> bool:
        """重置试用记录"""
        try:
            current_time = datetime.utcnow()
            doc_ref = db.collection('trial_records').document(client_ip)
            
            doc_ref.set({
                "ip": client_ip,
                "count": 0,
                "last_try": current_time,
                "created_at": current_time
            })
            return True
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
            if not trial_record or (current_time - trial_record["last_try"].replace(tzinfo=None)) > timedelta(days=14):
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