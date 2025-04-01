import uuid
from datetime import datetime
from datetime import timedelta

import bcrypt
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
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = "user") -> bool:
        users_collection = db.users

        # 检查用户名是否已存在
        if users_collection.find_one({'username': username}):
            return False

        # 检查邮箱是否已存在
        if users_collection.find_one({'email': email}):
            return False

        # 使用bcrypt加密密码
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # 创建用户文档
        users_collection.insert_one({
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'trial_count': 10,
            'trial_seconds': 60,
            'created_at': datetime.now()
        })
        return True

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
        admin = db.users.find_one({'_id': admin_id})
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
    async def get_user_usage_stats(user_id: str):
        try:
            user = db.users.find_one({'_id': user_id})
            if not user:
                return None

            return {
                'remaining_minutes': user.get('remaining_minutes', 0),
                'total_used_minutes': user.get('total_used_minutes', 0),
                'trial_count': user.get('trial_count', 0)
            }
        except Exception:
            return None

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
            user = db.users.find_one({'_id': user_id})
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
                {'_id': user_id},
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
            user = db.users.find_one({'_id': user_id})
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
                {'_id': user_id},
                {'$set': user_data}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return False

    @staticmethod
    async def get_user_wallet(user_id: str) -> dict:
        try:
            user = db.users.find_one({'_id': user_id})
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
            result = db.users.delete_one({'_id': user_id})
            return result.deleted_count > 0
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            return False

    @staticmethod
    def verify_password(user_id: str, password: str) -> bool:
        """验证用户密码"""
        try:
            user = db.users.find_one({'_id': user_id})
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
                {'_id': user_id},
                {'$set': {'password_hash': password_hash}}
            )
            return result.modified_count > 0
        except Exception as e:
            print(f"更新密码失败: {str(e)}")
            return False