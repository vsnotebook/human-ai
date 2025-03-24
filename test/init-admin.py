# 在Python交互式环境中执行
from services.firestore_service import FirestoreService

FirestoreService.create_user("admin", "admin@example.com", "admin123", role="admin")
