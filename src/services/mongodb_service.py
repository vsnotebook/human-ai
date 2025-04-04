import uuid
from datetime import datetime
from datetime import timedelta
from typing import Dict, Optional, Any

import bcrypt
from bson import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

from src.config.plans import SUBSCRIPTION_PLANS
from src.core.config import settings

# MongoDB 连接
uri = "mongodb+srv://vswork666:VuSnbgmkrs4jamVt@cluster0.naywsqs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
# uri = settings.MONGODB_URL
client = MongoClient(uri, server_api=ServerApi('1'))
db = client.voice_workshop

class MongoDBService:
    c_db = client.voice_workshop
    @staticmethod
    def create_user(username: str, email: str, password: str = None, role: str = "user", is_google_user: bool = False) -> bool:
        users_collection = db.users

        # 检查用户名是否已存在
        if users_collection.find_one({'username': username}):
            return False

        # 检查邮箱是否已存在
        if users_collection.find_one({'email': email}):
            return False

        # 创建用户文档
        user_data = {
            'username': username,
            'email': email,
            'role': role,
            'trial_count': 10,
            'trial_seconds': 60,
            'created_at': datetime.now(),
            'is_google_user': is_google_user,
            'google_id': None
        }

        # 如果不是谷歌用户，添加密码
        if not is_google_user and password:
            user_data['password_hash'] = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        result = users_collection.insert_one(user_data)
        return str(result.inserted_id) if result.inserted_id else False

    @staticmethod
    def verify_user(username: str, password: str) -> dict:
        users_collection = db.users
        user = users_collection.find_one({'username': username})

        if user:
            # 使用bcrypt验证密码
            if 'password_hash' in user:
                stored_hash = user['password_hash']
                if isinstance(stored_hash, bytes):
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
                else:
                    is_valid = False

                if is_valid:
                    return {
                        'id': str(user['_id']),
                        'username': user['username'],
                        'email': user['email'],
                        'role': user.get('role', 'user'),
                        'trial_count': user.get('trial_count', 10),
                        'trial_seconds': user.get('trial_seconds', 60)
                    }
        return None

    @staticmethod
    def get_all_users(admin_id: str):
        admin = db.users.find_one({'_id': ObjectId(admin_id)})
        if not admin or admin['role'] != 'admin':
            return None

        users = []
        for user in db.users.find():
            users.append({
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user['role'],
                'trial_count': user['trial_count'],
                'created_at': user['created_at']
            })
        return users

    @staticmethod
    async def get_dashboard_stats():
        try:
            total_users = db.users.count_documents({})

            # 获取今日转写次数
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_transcriptions = db.transcriptions.count_documents({
                'created_at': {'$gte': today_start}
            })

            return {
                'total_users': total_users,
                'today_transcriptions': today_transcriptions,
                'active_subscriptions': 0,
                'monthly_revenue': 0
            }
        except Exception:
            return {
                'total_users': 0,
                'today_transcriptions': 0,
                'active_subscriptions': 0,
                'monthly_revenue': 0
            }

    @staticmethod
    async def get_recent_activities():
        try:
            activities = list(db.activities.find().sort('created_at', -1).limit(10))
            return [{
                'username': activity.get('username'),
                'action': activity.get('action'),
                'created_at': activity.get('created_at')
            } for activity in activities]
        except Exception:
            return []

    @staticmethod
    async def create_order(user_id: str, plan_id: str):
        if plan_id not in SUBSCRIPTION_PLANS:
            raise ValueError("Invalid plan ID")

        plan = SUBSCRIPTION_PLANS[plan_id]
        order_id = str(uuid.uuid4())

        order_data = {
            'id': order_id,
            'user_id': user_id,
            'plan_id': plan_id,
            'plan_name': plan['name'],
            'amount': plan['price'],
            'minutes': plan['minutes'],
            'duration': plan['duration'],
            'status': 'pending',
            'created_at': datetime.now()
        }

        # 保存订单到 MongoDB
        db.orders.insert_one(order_data)
        return order_data

    @staticmethod
    async def activate_subscription(user_id: str, order_id: str):
        try:
            # 获取订单信息
            order = db.orders.find_one({'id': order_id})
            if not order or order['status'] != 'paid':
                return False

            # 更新用户订阅信息
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return False

            current_minutes = user.get('remaining_minutes', 0)

            # 计算新的到期时间
            current_expiry = user.get('subscription_expiry')
            if current_expiry and datetime.fromisoformat(current_expiry) > datetime.now():
                new_expiry = datetime.fromisoformat(current_expiry) + timedelta(days=30 * order['duration'])
            else:
                new_expiry = datetime.now() + timedelta(days=30 * order['duration'])

            # 更新用户数据
            db.users.update_one(
                {'_id': ObjectId(user_id)},
                {
                    '$set': {
                        'remaining_minutes': current_minutes + order['minutes'],
                        'subscription_expiry': new_expiry.isoformat(),
                        'subscription_plan': order['plan_id']
                    }
                }
            )

            # 记录订阅历史
            db.subscription_history.insert_one({
                'user_id': user_id,
                'order_id': order_id,
                'plan_id': order['plan_id'],
                'minutes_added': order['minutes'],
                'created_at': datetime.now()
            })

            return True

        except Exception as e:
            print(f"激活订阅失败: {str(e)}")
            return False

    @staticmethod
    async def get_order_status(order_id: str):
        try:
            order = db.orders.find_one({'id': order_id})
            if not order:
                return "not_found"
            return order.get('status', 'pending')
        except Exception:
            return "error"

    @staticmethod
    async def get_user_by_id(user_id):
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return None

            user_data = dict(user)
            user_data['id'] = str(user_data.pop('_id'))

            # 确保所有字段都是可序列化的
            for key, value in user_data.items():
                if isinstance(value, bytes):
                    user_data[key] = value.decode('utf-8', errors='replace')

            return user_data
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None

    @staticmethod
    async def update_user(user_id, user_data):
        try:
            # 如果包含密码，则使用bcrypt加密
            if 'password' in user_data and user_data['password']:
                password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
                user_data['password_hash'] = password_hash
                del user_data['password']

            result = db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': user_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return False

    @staticmethod
    async def get_user_wallet(user_id: str) -> dict:
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return {"balance": 0}

            return {
                "balance": user.get('balance', 0),
                "remaining_minutes": user.get('remaining_minutes', 0),
                "subscription_expiry": user.get('subscription_expiry', None)
            }
        except Exception as e:
            print(f"获取钱包信息失败: {str(e)}")
            return {"balance": 0}

    @staticmethod
    async def get_user_transactions(user_id: str) -> list:
        try:
            transactions = list(db.transactions
                             .find({'user_id': user_id})
                             .sort('created_at', -1)
                             .limit(20))

            return [{
                'id': str(trans['_id']),
                'amount': trans.get('amount', 0),
                'type': trans.get('type', ''),
                'description': trans.get('description', ''),
                'created_at': trans.get('created_at', datetime.now())
            } for trans in transactions]
        except Exception as e:
            print(f"获取交易记录失败: {str(e)}")
            return []

    @staticmethod
    async def get_user_subscriptions(user_id: str):
        try:
            subs = list(db.subscriptions.find({'user_id': user_id}))
            return [{
                'id': str(sub.get('_id')),
                'plan_name': sub.get('plan_name'),
                'minutes': sub.get('minutes'),
                'start_date': sub.get('start_date'),
                'end_date': sub.get('end_date'),
                'status': sub.get('status')
            } for sub in subs]
        except Exception:
            return []

    @staticmethod
    async def get_user_orders(user_id: str):
        try:
            orders = list(db.orders.find({'user_id': user_id}))
            return [{
                'id': str(order.get('_id')),
                'plan_name': order.get('plan_name'),
                'amount': order.get('amount'),
                'status': order.get('status'),
                'created_at': order.get('created_at')
            } for order in orders]
        except Exception:
            return []

    @staticmethod
    async def create_user_by_admin(username, email, password, role="user", trial_count=10):
        """管理员创建用户"""
        try:
            # 检查用户名是否存在
            existing_user = db.users.find_one({'username': username})
            if existing_user:
                return False

            # 检查邮箱是否存在
            existing_email = db.users.find_one({'email': email})
            if existing_email:
                return False

            # 使用bcrypt加密密码
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            user_data = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'role': role,
                'trial_count': trial_count,
                'created_at': datetime.now()
            }

            db.users.insert_one(user_data)
            return True
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            return False

    @staticmethod
    async def delete_user(user_id):
        """删除用户"""
        try:
            result = db.users.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            return False

    @staticmethod
    def verify_password(user_id: str, password: str) -> bool:
        """验证用户密码"""
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return False

            # 使用bcrypt验证密码
            if 'password_hash' in user:
                stored_hash = user['password_hash']
                if isinstance(stored_hash, bytes):
                    return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
            return False
        except Exception as e:
            print(f"验证密码失败: {str(e)}")
            return False

    @staticmethod
    async def update_password(user_id: str, new_password: str) -> bool:
        """更新用户密码"""
        try:
            # 使用bcrypt加密新密码
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

            # 更新密码
            result = db.users.update_one(
                {'_id': ObjectId(user_id)},
                {'$set': {'password_hash': password_hash}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新密码失败: {str(e)}")
            return False

    @staticmethod
    def get_user_by_email(email: str) -> dict:
        """Get user by email address"""
        try:
            user = db.users.find_one({'email': email})
            if not user:
                return None
            return {
                'id': str(user['_id']),
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user'),
                'trial_count': user.get('trial_count', 10),
                'trial_seconds': user.get('trial_seconds', 60)
            }
        except Exception as e:
            print(f"Failed to get user by email: {str(e)}")
            return None

    # 在MongoDBService类中添加get_user_by_username方法
    @classmethod
    def get_user_by_username(cls, username: str) -> Optional[Dict]:
        """根据用户名获取用户信息"""
        try:
            user = db.users.find_one({"username": username})
            if not user:
                return None
            
            # 转换ObjectId为字符串
            user_data = dict(user)
            user_data['id'] = str(user_data.pop('_id'))
            
            # 确保所有字段都是可序列化的
            for key, value in user_data.items():
                if isinstance(value, bytes):
                    user_data[key] = value.decode('utf-8', errors='replace')
                    
            return user_data
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None
    # 在适当的位置添加以下方法
    
    @classmethod
    async def create_user_balance(cls, user_id, initial_balance=None):
        """创建用户余额记录，包含初始赠送额度"""
        if initial_balance is None:
            initial_balance = {
                "asr_balance": 60,  # 1分钟语音识别 (单位:秒)
                "tts_balance": 500,  # 500个字符合成
                "text_translation_balance": 0,
                "voice_translation_balance": 0
            }
        
        balance_data = {
            "user_id": user_id,
            **initial_balance,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        cls.c_db.user_balance.insert_one(balance_data)
        return balance_data
    
    @classmethod
    async def get_user_usage_stats(cls, user_id):
        """获取用户使用统计和余额信息"""
        # 获取用户基本信息
        user = db.users.find_one({'_id': ObjectId(user_id)})
        if not user:
            return None

        # 获取用户余额信息
        balance = cls.c_db.user_balance.find_one({"user_id": user_id})
        if not balance:
            # 如果没有余额记录，创建一个新的
            balance = await cls.create_user_balance(user_id)
        
        # 合并所有统计数据
        stats = {
            'remaining_minutes': user.get('remaining_minutes', 0),
            'total_used_minutes': user.get('total_used_minutes', 0),
            'trial_count': user.get('trial_count', 0),
            "asr_balance": balance.get("asr_balance", 0),
            "tts_balance": balance.get("tts_balance", 0),
            "text_translation_balance": balance.get("text_translation_balance", 0),
            "voice_translation_balance": balance.get("voice_translation_balance", 0)
        }
        
        return stats

    @staticmethod
    async def get_user_usage_stats2(user_id: str):
        try:
            user = db.users.find_one({'_id': ObjectId(user_id)})
            if not user:
                return None

            return {
                'remaining_minutes': user.get('remaining_minutes', 0),
                'total_used_minutes': user.get('total_used_minutes', 0),
                'trial_count': user.get('trial_count', 0)
            }
        except Exception:
            return None
    
    @classmethod
    async def update_user_balance(cls, user_id, plan_id):
        """根据购买的套餐更新用户余额"""
        # 获取套餐详情
        plan = SUBSCRIPTION_PLANS.get(plan_id)
        if not plan:
            return False
        
        # 获取当前余额
        current_balance = await cls.get_user_balance(user_id)
        
        # 根据套餐类型更新相应的余额
        updates = {}
        if "asr_minutes" in plan:
            updates["asr_balance"] = current_balance.get("asr_balance", 0) + (plan["asr_minutes"] * 60)
        
        if "tts_characters" in plan:
            updates["tts_balance"] = current_balance.get("tts_balance", 0) + plan["tts_characters"]
        
        if "text_translation_count" in plan:
            updates["text_translation_balance"] = current_balance.get("text_translation_balance", 0) + plan["text_translation_count"]
        
        if "voice_translation_minutes" in plan:
            updates["voice_translation_balance"] = current_balance.get("voice_translation_balance", 0) + (plan["voice_translation_minutes"] * 60)
        
        if updates:
            updates["updated_at"] = datetime.now()
            await cls.c_db.user_balance.update_one(
                {"user_id": user_id},
                {"$set": updates}
            )
            return True
        
        return False
    
    @classmethod
    async def get_order_details(cls, order_id):
        """获取订单详情"""
        order = await cls.c_db.orders.find_one({"id": order_id})
        return order
    
    @classmethod
    async def register_user(cls, username, email, password_hash):
        """注册用户并创建初始余额"""
        # 现有的用户注册代码
        user_id = 1# ... 获取新创建的用户ID
        
        # 创建用户余额记录
        await cls.create_user_balance(user_id)
        
        return user_id

    @classmethod
    async def deduct_audio_time(cls, user_id: str, audio_duration_seconds: int) -> Dict[str, Any]:
        """扣除用户的语音识别时长余额"""
        try:
            # 获取用户当前余额信息
            balance = cls.c_db.user_balance.find_one({'user_id': user_id})
            if not balance:
                # 如果没有余额记录，创建一个新的
                balance = await cls.create_user_balance(user_id)
            
            # 计算剩余时长
            remaining_seconds = balance.get("asr_balance", 0)
            if remaining_seconds < audio_duration_seconds:
                raise ValueError("语音识别时长余额不足")
            
            # 扣除时长
            new_remaining_seconds = remaining_seconds - audio_duration_seconds
            
            # 更新用户余额信息
            update_result = cls.c_db.user_balance.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "asr_balance": new_remaining_seconds,
                        "updated_at": datetime.now()
                    },
                    "$inc": {
                        "total_asr_usage_seconds": audio_duration_seconds
                    }
                }
            )
            
            if update_result.modified_count == 0:
                raise ValueError("更新用户余额失败")
            
            # 返回更新后的用户余额信息
            return cls.c_db.user_balance.find_one({"user_id": user_id})
        except Exception as e:
            print(f"扣除语音识别时长失败: {str(e)}")
            raise

    @classmethod
    def create_api_key(cls, user_id: str) -> Dict:
        """为用户创建新的API密钥"""
        from src.utils.auth_util import generate_api_secret

        # 生成API密钥
        api_secret = generate_api_secret()

        # 创建API密钥记录
        api_key = {
            "user_id": user_id,
            "api_secret": api_secret,
            "created_at": datetime.utcnow(),
            "last_used_at": None,
            "is_active": True
        }

        # 保存到数据库
        result = db.api_keys.insert_one(api_key)
        api_key["_id"] = str(result.inserted_id)

        return api_key

    @classmethod
    def get_user_api_keys(cls, user_id: str) -> list:
        """获取用户的所有API密钥"""
        api_keys = list(db.api_keys.find({"user_id": user_id}))
        for key in api_keys:
            key["_id"] = str(key["_id"])
        return api_keys

    @classmethod
    def get_api_secret(cls, username: str) -> Optional[str]:
        """根据用户名获取API密钥"""
        # 先获取用户ID
        user = db.users.find_one({"username": username})
        if not user:
            return None

        # 获取用户的活跃API密钥
        api_key = db.api_keys.find_one({
            "user_id": str(user["_id"]),
            "is_active": True
        })

        if not api_key:
            return None

        # 更新最后使用时间
        db.api_keys.update_one(
            {"_id": api_key["_id"]},
            {"$set": {"last_used_at": datetime.utcnow()}}
        )

        return api_key["api_secret"]

    @classmethod
    def deactivate_api_key(cls, key_id: str, user_id: str) -> bool:
        """停用API密钥"""
        result = db.api_keys.update_one(
            {"_id": ObjectId(key_id), "user_id": user_id},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

    @classmethod
    def insert_usage_records(cls, usage_record: dict) :
        db.usage_records.insert_one(usage_record)
