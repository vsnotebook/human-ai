from pydantic import BaseSettings

class Settings(BaseSettings):
    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # 阿里云配置
    ALIYUN_ACCESS_KEY_ID: str = ""
    ALIYUN_ACCESS_KEY_SECRET: str = ""
    ALIYUN_APP_KEY: str = ""
    
    # 默认服务提供商
    DEFAULT_SPEECH_PROVIDER: str = "google"
    DEFAULT_TRANSLATE_PROVIDER: str = "google"
    DEFAULT_TTS_PROVIDER: str = "google"


settings = Settings()  # 全局配置实例
