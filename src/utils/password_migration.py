import hashlib
import bcrypt
from google.cloud import firestore
from src.core.config import settings

db = firestore.Client(project=settings.PROJECT_ID)

async def migrate_passwords():
    """将旧格式密码迁移到bcrypt格式"""
    users_ref = db.collection('users')
    users = users_ref.get()
    
    migrated_count = 0
    for user in users:
        user_data = user.to_dict()
        user_id = user.id
        
        # 检查是否有旧格式密码
        if 'password_hash' in user_data and 'salt' in user_data:
            if isinstance(user_data['password_hash'], bytes) and not user_data.get('is_bcrypt', False):
                try:
                    # 这里需要知道原始密码才能迁移，实际情况可能需要让用户重置密码
                    # 或者在用户下次登录时自动迁移
                    print(f"需要迁移用户 {user_data['username']} 的密码")
                except Exception as e:
                    print(f"迁移用户 {user_data['username']} 密码失败: {str(e)}")
        
    print(f"成功迁移 {migrated_count} 个用户密码")

# 在需要时运行此函数
# migrate_passwords()