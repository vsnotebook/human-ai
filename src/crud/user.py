from typing import Optional
from datetime import datetime
# from firebase_admin import auth
from src.db.firebase import db
from src.schemas.user import UserCreate, UserUpdate, UserInDB
# from src.core.security import get_password_hash, verify_password

class UserCRUD:
    @staticmethod
    async def create(user: UserCreate) -> Optional[UserInDB]:
        try:
            # 检查用户名是否存在
            users_ref = db.collection('users')
            existing_user = users_ref.where('username', '==', user.username).get()
            if len(existing_user) > 0:
                return None

            # 创建用户
            user_data = user.model_dump()
            # user_data['password'] = get_password_hash(user_data['password'])
            user_data['password'] = user_data['password']
            user_data['created_at'] = datetime.now()
            
            doc_ref = users_ref.document()
            user_data['id'] = doc_ref.id
            doc_ref.set(user_data)
            
            return UserInDB(**user_data)
        except Exception as e:
            print(f"创建用户失败: {str(e)}")
            return None

    @staticmethod
    async def get_by_username(username: str) -> Optional[UserInDB]:
        try:
            users_ref = db.collection('users')
            users = users_ref.where('username', '==', username).get()
            if len(users) == 0:
                return None
            
            user_data = users[0].to_dict()
            user_data['id'] = users[0].id
            return UserInDB(**user_data)
        except Exception as e:
            print(f"获取用户失败: {str(e)}")
            return None

    @staticmethod
    async def update(user_id: str, user_update: UserUpdate) -> Optional[UserInDB]:
        try:
            user_ref = db.collection('users').document(user_id)
            user = user_ref.get()
            if not user.exists:
                return None

            update_data = user_update.model_dump(exclude_unset=True)
            if 'password' in update_data:
                update_data['password'] = get_password_hash(update_data['password'])

            user_ref.update(update_data)
            
            updated_user = user_ref.get()
            user_data = updated_user.to_dict()
            user_data['id'] = user_id
            return UserInDB(**user_data)
        except Exception as e:
            print(f"更新用户失败: {str(e)}")
            return None

    @staticmethod
    async def authenticate(username: str, password: str) -> Optional[UserInDB]:
        user = await UserCRUD.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password):
            return None
        return user