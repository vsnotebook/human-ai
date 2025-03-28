import hashlib
import os
import uuid
import bcrypt
from datetime import datetime
from datetime import timedelta

from google.cloud import firestore
from google.cloud.firestore import Client

from src.config.plans import SUBSCRIPTION_PLANS
from src.core.config import settings

db: Client = firestore.Client(project=settings.PROJECT_ID)


class FirestoreService:
    @staticmethod
    def create_user(username: str, email: str, password: str, role: str = "user") -> bool:
        users_ref = db.collection('users')

        # 检查用户名是否已存在
        if users_ref.where('username', '==', username).get():
            return False

        # 检查邮箱是否已存在
        if users_ref.where('email', '==', email).get():
            return False

        # 使用bcrypt加密密码
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        # 创建用户文档
        users_ref.add({
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'role': role,
            'trial_count': 10,
            'trial_seconds': 60,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return True

    @staticmethod
    def verify_user(username: str, password: str) -> dict:
        users_ref = db.collection('users')
        users = users_ref.where('username', '==', username).get()

        for user in users:
            user_data = user.to_dict()
            
            # 使用bcrypt验证密码
            if 'password_hash' in user_data:
                # 处理新的bcrypt格式
                stored_hash = user_data['password_hash']
                if isinstance(stored_hash, bytes):
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
                else:
                    # 兼容旧格式密码（如果有）
                    is_valid = False
                
                if is_valid:
                    return {
                        'id': user.id,
                        'username': user_data['username'],
                        'email': user_data['email'],
                        'role': user_data.get('role', 'user'),
                        'trial_count': user_data.get('trial_count', 10),
                        'trial_seconds': user_data.get('trial_seconds', 60)
                    }
        return None

    @staticmethod
    def get_all_users(admin_id: str):
        admin = db.collection('users').document(admin_id).get()
        if not admin.exists or admin.to_dict()['role'] != 'admin':
            return None

        users = []
        for user in db.collection('users').get():
            user_data = user.to_dict()
            users.append({
                'id': user.id,
                'username': user_data['username'],
                'email': user_data['email'],
                'role': user_data['role'],
                'trial_count': user_data['trial_count'],
                'created_at': user_data['created_at']
            })
        return users

    @staticmethod
    async def get_dashboard_stats():
        try:
            users = db.collection('users').get()
            total_users = len(users)

            # 获取今日转写次数
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            transcriptions = db.collection('transcriptions').where(
                'created_at', '>=', today_start
            ).get()

            return {
                'total_users': total_users,
                'today_transcriptions': len(transcriptions),
                'active_subscriptions': 0,  # 待实现订阅功能后更新
                'monthly_revenue': 0  # 待实现支付功能后更新
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
            activities = db.collection('activities').order_by(
                'created_at', direction=firestore.Query.DESCENDING
            ).limit(10).get()

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
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return None

            user_data = user.to_dict()
            return {
                'remaining_minutes': user_data.get('remaining_minutes', 0),
                'total_used_minutes': user_data.get('total_used_minutes', 0),
                'trial_count': user_data.get('trial_count', 0)
            }
        except Exception:
            return None

    @staticmethod
    async def get_user_subscriptions(user_id: str):
        try:
            subs = db.collection('subscriptions').where('user_id', '==', user_id).get()
            return [{
                'id': sub.id,
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
            orders = db.collection('orders').where('user_id', '==', user_id).get()
            return [{
                'id': order.id,
                'plan_name': order.get('plan_name'),
                'amount': order.get('amount'),
                'status': order.get('status'),
                'created_at': order.get('created_at')
            } for order in orders]
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

        # 保存订单到 Firestore
        db.collection('orders').document(order_id).set(order_data)

        return order_data

    @staticmethod
    async def activate_subscription(user_id: str, order_id: str):
        try:
            # 获取订单信息
            order_ref = db.collection('orders').document(order_id)
            order = order_ref.get()
            if not order.exists:
                return False

            order_data = order.to_dict()
            if order_data['status'] != 'paid':
                return False

            # 更新用户订阅信息
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return False

            user_data = user.to_dict()
            current_minutes = user_data.get('remaining_minutes', 0)

            # 计算新的到期时间
            current_expiry = user_data.get('subscription_expiry')
            if current_expiry and datetime.fromisoformat(current_expiry) > datetime.now():
                new_expiry = datetime.fromisoformat(current_expiry) + timedelta(days=30 * order_data['duration'])
            else:
                new_expiry = datetime.now() + timedelta(days=30 * order_data['duration'])

            # 更新用户数据
            user_ref.update({
                'remaining_minutes': current_minutes + order_data['minutes'],
                'subscription_expiry': new_expiry.isoformat(),
                'subscription_plan': order_data['plan_id']
            })

            # 记录订阅历史
            db.collection('subscription_history').add({
                'user_id': user_id,
                'order_id': order_id,
                'plan_id': order_data['plan_id'],
                'minutes_added': order_data['minutes'],
                'created_at': datetime.now()
            })

            return True

        except Exception as e:
            print(f"激活订阅失败: {str(e)}")
            return False

    @staticmethod
    @staticmethod
    async def get_order_status(order_id: str):
        try:
            order_ref = db.collection('orders').document(order_id)
            order = order_ref.get()
            if not order.exists:
                return "not_found"

            return order.to_dict().get('status', 'pending')
        except Exception:
            return "error"

    @staticmethod
    async def get_user_by_id(user_id):
        """根据ID获取用户信息"""
        try:
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return None
            
            user_data = user.to_dict()
            user_data['id'] = user_id
            
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
        """更新用户信息"""
        try:
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return False
            
            # 如果包含密码，则使用bcrypt加密
            if 'password' in user_data and user_data['password']:
                password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt())
                user_data['password_hash'] = password_hash
                del user_data['password']  # 删除明文密码
            
            user_ref.update(user_data)
            return True
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return False

    @staticmethod
    async def create_user_by_admin(username, email, password, role="user", trial_count=10):
        """管理员创建用户"""
        try:
            # 检查用户名是否存在
            users_ref = db.collection('users')
            existing_user = users_ref.where('username', '==', username).get()
            if len(existing_user) > 0:
                return False
            
            # 检查邮箱是否存在
            existing_email = users_ref.where('email', '==', email).get()
            if len(existing_email) > 0:
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
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return False
            
            user_ref.delete()
            return True
        except Exception as e:
            print(f"删除用户失败: {str(e)}")
            return False

    @staticmethod
    def verify_password(user_id: str, password: str) -> bool:
        """验证用户密码"""
        try:
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return False
            
            user_data = user.to_dict()
            
            # 使用bcrypt验证密码
            if 'password_hash' in user_data:
                stored_hash = user_data['password_hash']
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
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return False
            
            # 使用bcrypt加密新密码
            password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            
            # 更新密码
            user_ref.update({
                'password_hash': password_hash
            })
            return True
        except Exception as e:
            print(f"更新密码失败: {str(e)}")
            return False
    
    @staticmethod
    async def get_user_wallet(user_id: str) -> dict:
        """获取用户钱包信息"""
        try:
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return {"balance": 0}
            
            user_data = user.to_dict()
            return {
                "balance": user_data.get('balance', 0),
                "remaining_minutes": user_data.get('remaining_minutes', 0),
                "subscription_expiry": user_data.get('subscription_expiry', None)
            }
        except Exception as e:
            print(f"获取钱包信息失败: {str(e)}")
            return {"balance": 0}
    
    @staticmethod
    async def get_user_transactions(user_id: str) -> list:
        """获取用户交易记录"""
        try:
            transactions = db.collection('transactions').where('user_id', '==', user_id).order_by(
                'created_at', direction=firestore.Query.DESCENDING
            ).limit(20).get()
            
            return [{
                'id': trans.id,
                'amount': trans.to_dict().get('amount', 0),
                'type': trans.to_dict().get('type', ''),
                'description': trans.to_dict().get('description', ''),
                'created_at': trans.to_dict().get('created_at', datetime.now())
            } for trans in transactions]
        except Exception as e:
            print(f"获取交易记录失败: {str(e)}")
            return []
