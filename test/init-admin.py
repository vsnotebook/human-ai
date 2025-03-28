# 在Python交互式环境中执行
from src.core.config import settings
# import bcrypt
from src.services.firestore_service import FirestoreService

FirestoreService.create_user("admin2", "admin@example.com", "admin123", role="admin")
# 使用bcrypt加密密码
# password_hash = bcrypt.hashpw('111111'.encode('utf-8'), bcrypt.gensalt())


