# from pydantic_settings import BaseSettings
#
# class Settings(BaseSettings):
#     PROJECT_NAME: str = "Web Cloud"
#     DEBUG: bool = True
#     SERVER_HOST: str = "127.0.0.1"
#     SERVER_PORT: int = 8080
#     SECRET_KEY: str = "your-secret-key-here"
#
#     # Firebase配置
#     FIREBASE_CREDENTIALS: str = "path/to/firebase-credentials.json"
#
#     # 其他配置...
#
#     class Config:
#         env_file = ".env"
#
# settings = Settings()