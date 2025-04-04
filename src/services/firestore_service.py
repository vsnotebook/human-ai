import uuid
from datetime import datetime
from datetime import timedelta
from typing import Dict, Optional

import bcrypt
from google.cloud import firestore
from google.cloud.firestore import Client

from src.config.plans import SUBSCRIPTION_PLANS
from src.core.config import settings

db: Client = firestore.Client(project=settings.PROJECT_ID)


class FirestoreService:
    @staticmethod
    def create_user(username: str, email: str, password: str = None, role: str = "user", is_google_user: bool = False) -> bool:
        users_ref = db.collection('users')

        # 检查用户名是否已存在
        username_query = users_ref.where('username', '==', username).limit(1).get()
        if len(list(username_query)) > 0:
            return False

        # 检查邮箱是否已存在
        email_query = users_ref.where('email', '==', email).limit(1).get()
        if len(list(email_query)) > 0:
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

        try:
            doc_ref = users_ref.document()
            doc_ref.set(user_data)
            return doc_ref.id
        except Exception:
            return False

    @staticmethod
    def verify_user(username: str, password: str) -> dict:
        users_ref = db.collection('users')
        user_query = users_ref.where('username', '==', username).limit(1).get()
        
        for user_doc in user_query:
            user = user_doc.to_dict()
            user['id'] = user_doc.id

            # 使用bcrypt验证密码
            if 'password_hash' in user:
                stored_hash = user['password_hash']
                if isinstance(stored_hash, bytes):
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
                else:
                    is_valid = False

                if is_valid:
                    return {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'role': user.get('role', 'user'),
                        'trial_count': user.get('trial_count', 10),
                        'trial_seconds': user.get('trial_seconds', 60)
                    }
        return None

    @staticmethod
    def get_all_users(admin_id: str):
        admin_doc = db.collection('users').document(admin_id).get()
        if not admin_doc.exists or admin_doc.to_dict().get('role') != 'admin':
            return None

        users = []
        for user_doc in db.collection('users').stream():
            user = user_doc.to_dict()
            users.append({
                'id': user_doc.id,
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
            users_ref = db.collection('users')
            total_users = len(list(users_ref.stream()))

            # 获取今日转写次数
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            
            transcriptions_ref = db.collection('transcriptions')
            today_query = transcriptions_ref.where('created_at', '>=', today_start).get()
            today_transcriptions = len(list(today_query))

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
            activities_ref = db.collection('activities')
            activities_query = activities_ref.order_by('created_at', direction=firestore.Query.DESCENDING).limit(10)
            activities = []
            for doc in activities_query.stream():
                activity = doc.to_dict()
                activities.append({
                    'username': activity.get('username'),
                    'action': activity.get('action'),
                    'created_at': activity.get('created_at')
                })
            return activities
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

        try:
            db.collection('orders').document(order_id).set(order_data)
            return order_data
        except Exception:
            return None

    @staticmethod
    async def activate_subscription(user_id: str, order_id: str):
        try:
            # 获取订单信息
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return False
            
            order = order_doc.to_dict()
            if order['status'] != 'paid':
                return False

            # 更新用户订阅信息
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return False

            user = user_doc.to_dict()
            current_minutes = user.get('remaining_minutes', 0)

            # 计算新的到期时间
            current_expiry = user.get('subscription_expiry')
            if current_expiry and datetime.fromisoformat(current_expiry) > datetime.now():
                new_expiry = datetime.fromisoformat(current_expiry) + timedelta(days=30 * order['duration'])
            else:
                new_expiry = datetime.now() + timedelta(days=30 * order['duration'])

            # 更新用户数据
            db.collection('users').document(user_id).update({
                'remaining_minutes': current_minutes + order['minutes'],
                'subscription_expiry': new_expiry.isoformat(),
                'subscription_plan': order['plan_id']
            })

            # 记录订阅历史
            subscription_data = {
                'user_id': user_id,
                'order_id': order_id,
                'plan_id': order['plan_id'],
                'minutes_added': order['minutes'],
                'created_at': datetime.now()
            }
            db.collection('subscription_history').add(subscription_data)

            return True
        except Exception as e:
            print(f"激活订阅失败: {str(e)}")
            return False

    @staticmethod
    async def get_order_status(order_id: str):
        try:
            order_doc = db.collection('orders').document(order_id).get()
            if not order_doc.exists:
                return "not_found"
            return order_doc.to_dict().get('status', 'pending')
        except Exception:
            return "error"

    @staticmethod
    async def get_user_by_id(user_id):
        try:
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return None

            user_data = user_doc.to_dict()
            user_data['id'] = user_doc.id

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
            if 'password' in user_data and user_data['password']:
                password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
                user_data['password_hash'] = password_hash
                del user_data['password']

            db.collection('users').document(user_id).update(user_data)
            return True
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return False

    @staticmethod
    async def get_user_wallet(user_id: str) -> dict:
        try:
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return {"balance": 0}

            user = user_doc.to_dict()
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
            transactions_ref = db.collection('transactions')
            query = transactions_ref.where('user_id', '==', user_id)\
                                  .order_by('created_at', direction=firestore.Query.DESCENDING)\
                                  .limit(20)
            
            transactions = []
            for doc in query.stream():
                trans = doc.to_dict()
                transactions.append({
                    'id': doc.id,
                    'amount': trans.get('amount', 0),
                    'type': trans.get('type', ''),
                    'description': trans.get('description', ''),
                    'created_at': trans.get('created_at', datetime.now())
                })
            return transactions
        except Exception as e:
            print(f"获取交易记录失败: {str(e)}")
            return []

    @staticmethod
    async def get_user_subscriptions(user_id: str):
        try:
            subs_ref = db.collection('subscriptions')
            query = subs_ref.where('user_id', '==', user_id)
            
            subscriptions = []
            for doc in query.stream():
                sub = doc.to_dict()
                subscriptions.append({
                    'id': doc.id,
                    'plan_name': sub.get('plan_name'),
                    'minutes': sub.get('minutes'),
                    'start_date': sub.get('start_date'),
                    'end_date': sub.get('end_date'),
                    'status': sub.get('status')
                })
            return subscriptions
        except Exception:
            return []

    @staticmethod
    async def get_user_orders(user_id: str):
        try:
            orders_ref = db.collection('orders')
            query = orders_ref.where('user_id', '==', user_id)
            
            orders = []
            for doc in query.stream():
                order = doc.to_dict()
                orders.append({
                    'id': doc.id,
                    'plan_name': order.get('plan_name'),
                    'amount': order.get('amount'),
                    'status': order.get('status'),
                    'created_at': order.get('created_at')
                })
            return orders
        except Exception:
            return []

    @staticmethod
    async def create_user_by_admin(username, email, password, role="user", trial_count=10):
        """管理员创建用户"""
        try:
            users_ref = db.collection('users')

            # 检查用户名是否存在
            username_query = users_ref.where('username', '==', username).limit(1).get()
            if len(list(username_query)) > 0:
                return False

            # 检查邮箱是否存在
            email_query = users_ref.where('email', '==', email).limit(1).get()
            if len(list(email_query)) > 0:
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

            users_ref.add(user_data)
            return True
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            return False

    @staticmethod
    async def delete_user(user_id):
        """删除用户"""
        try:
            db.collection('users').document(user_id).delete()
            return True
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            return False

    @staticmethod
    def verify_password(user_id: str, password: str) -> bool:
        """验证用户密码"""
        try:
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return False

            user = user_doc.to_dict()
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
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            db.collection('users').document(user_id).update({
                'password_hash': password_hash
            })
            return True
        except Exception as e:
            print(f"更新密码失败: {str(e)}")
            return False

    @staticmethod
    def get_user_by_email(email: str) -> dict:
        """Get user by email address"""
        try:
            users_ref = db.collection('users')
            query = users_ref.where('email', '==', email).limit(1).get()
            
            for doc in query:
                user = doc.to_dict()
                return {
                    'id': doc.id,
                    'username': user['username'],
                    'email': user['email'],
                    'role': user.get('role', 'user'),
                    'trial_count': user.get('trial_count', 10),
                    'trial_seconds': user.get('trial_seconds', 60)
                }
            return None
        except Exception as e:
            print(f"Failed to get user by email: {str(e)}")
            return None

    @classmethod
    def get_user_by_username(cls, username: str) -> Optional[Dict]:
        """根据用户名获取用户信息"""
        try:
            users_ref = db.collection('users')
            query = users_ref.where('username', '==', username).limit(1).get()
            
            for doc in query:
                user_data = doc.to_dict()
                user_data['id'] = doc.id
                
                # 确保所有字段都是可序列化的
                for key, value in user_data.items():
                    if isinstance(value, bytes):
                        user_data[key] = value.decode('utf-8', errors='replace')
                        
                return user_data
            return None
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None

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
        
        try:
            db.collection('user_balance').document(user_id).set(balance_data)
            return balance_data
        except Exception:
            return None

    @classmethod
    async def get_user_usage_stats(cls, user_id):
        """获取用户使用统计和余额信息"""
        try:
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return None

            user = user_doc.to_dict()
            balance_doc = db.collection('user_balance').document(user_id).get()
            
            if not balance_doc.exists:
                balance = await cls.create_user_balance(user_id)
            else:
                balance = balance_doc.to_dict()
            
            return {
                'remaining_minutes': user.get('remaining_minutes', 0),
                'total_used_minutes': user.get('total_used_minutes', 0),
                'trial_count': user.get('trial_count', 0),
                "asr_balance": balance.get("asr_balance", 0),
                "tts_balance": balance.get("tts_balance", 0),
                "text_translation_balance": balance.get("text_translation_balance", 0),
                "voice_translation_balance": balance.get("voice_translation_balance", 0)
            }
        except Exception:
            return None

    @staticmethod
    async def get_user_usage_stats2(user_id: str):
        try:
            user_doc = db.collection('users').document(user_id).get()
            if not user_doc.exists:
                return None

            user = user_doc.to_dict()
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
        try:
            plan = SUBSCRIPTION_PLANS.get(plan_id)
            if not plan:
                return False
            
            balance_doc = db.collection('user_balance').document(user_id).get()
            if not balance_doc.exists:
                current_balance = await cls.create_user_balance(user_id)
            else:
                current_balance = balance_doc.to_dict()
            
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
                db.collection('user_balance').document(user_id).update(updates)
                return True
            
            return False
        except Exception:
            return False

    @classmethod
    async def get_order_details(cls, order_id):
        """获取订单详情"""
        try:
            order_doc = db.collection('orders').document(order_id).get()
            return order_doc.to_dict() if order_doc.exists else None
        except Exception:
            return None

    @classmethod
    async def register_user(cls, username, email, password_hash):
        """注册用户并创建初始余额"""
        try:
            # 创建用户文档
            user_ref = db.collection('users').document()
            user_data = {
                'username': username,
                'email': email,
                'password_hash': password_hash,
                'created_at': datetime.now()
            }
            user_ref.set(user_data)
            
            # 创建用户余额记录
            await cls.create_user_balance(user_ref.id)
            
            return user_ref.id
        except Exception:
            return None

    @classmethod
    def create_api_key(cls, user_id: str) -> Dict:
        """为用户创建新的API密钥"""
        from src.utils.auth_util import generate_api_secret

        try:
            api_secret = generate_api_secret()
            api_key = {
                "user_id": user_id,
                "api_secret": api_secret,
                "created_at": datetime.utcnow(),
                "last_used_at": None,
                "is_active": True
            }

            doc_ref = db.collection('api_keys').document()
            doc_ref.set(api_key)
            api_key["id"] = doc_ref.id

            return api_key
        except Exception:
            return None

    @classmethod
    def get_user_api_keys(cls, user_id: str) -> list:
        """获取用户的所有API密钥"""
        try:
            api_keys = []
            query = db.collection('api_keys').where('user_id', '==', user_id)
            for doc in query.stream():
                key = doc.to_dict()
                key["id"] = doc.id
                api_keys.append(key)
            return api_keys
        except Exception:
            return []

    @classmethod
    def get_api_secret(cls, username: str) -> Optional[str]:
        """根据用户名获取API密钥"""
        try:
            # 先获取用户ID
            user_query = db.collection('users').where('username', '==', username).limit(1).get()
            user_docs = list(user_query)
            if not user_docs:
                return None
            
            user_id = user_docs[0].id

            # 获取用户的活跃API密钥
            api_key_query = db.collection('api_keys').where('user_id', '==', user_id)\
                                                   .where('is_active', '==', True)\
                                                   .limit(1).get()
            api_key_docs = list(api_key_query)
            if not api_key_docs:
                return None

            api_key = api_key_docs[0]
            
            # 更新最后使用时间
            api_key.reference.update({
                "last_used_at": datetime.utcnow()
            })

            return api_key.to_dict()["api_secret"]
        except Exception:
            return None

    @classmethod
    def deactivate_api_key(cls, key_id: str, user_id: str) -> bool:
        """停用API密钥"""
        try:
            doc_ref = db.collection('api_keys').document(key_id)
            doc = doc_ref.get()
            
            if not doc.exists or doc.to_dict()['user_id'] != user_id:
                return False
                
            doc_ref.update({"is_active": False})
            return True
        except Exception:
            return False

