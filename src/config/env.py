import os
from pydantic import BaseSettings, Field, RedisDsn,PostgresDsn
from typing import Optional

class Settings(BaseSettings):
    # 通用配置
    # ENV: str = Field(..., env="ENV")  # 当前环境（dev/test/prod）
    ENV: str
    DEBUG: bool = False
    PROJECT_ID: str
    REGION: str
    CREDENTIALS_PATH: str
    SERVER_HOST: str
    SERVER_PORT: str
    http_proxy: str
    https_proxy: str

    # 安全配置
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = {
            "dev": "envs/.env.dev",
            "test": "envs/.env.test",
            "prod": "envs/.env.prod",
        }[os.getenv("ENV", "dev")]  # 根据 ENV 变量选择配置文件
        env_file_encoding = 'utf-8'

    def __init__(self, **values):
        super().__init__(**values)
        # 动态生成数据库 URL
        self.SQLALCHEMY_DATABASE_URI = (
            f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )
        self.pg_dsn_URI = 'postgres://user:pass@localhost:5432/foobar'

settings = Settings()  # 全局配置实例









