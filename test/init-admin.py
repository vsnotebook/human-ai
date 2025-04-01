# 在Python交互式环境中执行
from src.core.config import settings
# import bcrypt


def init_admin_firestore():
    from src.services.firestore_service import FirestoreService
    FirestoreService.create_user("admin2", "admin@example.com", "admin123", role="admin")




def init_admin_mongo():
    from src.services.mongodb_service import MongoDBService
    MongoDBService.create_user("admin", "admin@example.com", "admin123", role="admin")


init_admin_mongo()
# init_admin_firestore()

# 使用bcrypt加密密码
# password_hash = bcrypt.hashpw('111111'.encode('utf-8'), bcrypt.gensalt())


