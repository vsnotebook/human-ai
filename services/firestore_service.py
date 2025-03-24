from google.cloud import firestore
from google.cloud.firestore import Client
import hashlib
import os

from env import PROJECT_ID

db: Client = firestore.Client(project=PROJECT_ID)

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
            
        # 密码加盐哈希
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        
        # 创建用户文档
        users_ref.add({
            'username': username,
            'email': email,
            'password_hash': password_hash,
            'salt': salt,
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
            password_hash = hashlib.pbkdf2_hmac(
                'sha256',
                password.encode('utf-8'),
                user_data['salt'],
                100000
            )
            
            if password_hash == user_data['password_hash']:
                return {
                    'id': user.id,
                    'username': user_data['username'],
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'trial_count': user_data['trial_count'],
                    'trial_seconds': user_data['trial_seconds']
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