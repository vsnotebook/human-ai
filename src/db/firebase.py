# import firebase_admin
# from firebase_admin import credentials, firestore
# from src.core.config import settings

from google.cloud import firestore
from google.cloud.firestore import Client

from src.env import PROJECT_ID

db: Client = firestore.Client(project=PROJECT_ID)

# def init_firebase():
#     """初始化 Firebase 连接"""
#     try:
#         cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS)
#         firebase_admin.initialize_app(cred)
#         return firestore.client()
#     except Exception as e:
#         print(f"Firebase 初始化失败: {str(e)}")
#         raise
#
# db = init_firebase()