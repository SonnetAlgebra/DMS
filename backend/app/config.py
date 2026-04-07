"""应用配置"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用设置"""

    app_name: str = "DMS API"
    app_version: str = "1.0.0"
    debug: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
