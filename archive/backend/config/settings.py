"""应用配置 - 使用pydantic BaseSettings从环境变量读取"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # 数据库
    database_url: str = "postgresql+asyncpg://ecommerce:ecommerce_dev@localhost:5432/ecommerce_agent"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "ecommerce_agent"
    db_user: str = "ecommerce"
    db_password: str = "ecommerce_dev"

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_host: str = "localhost"
    redis_port: int = 6379

    # Agnes AI API
    agnes_api_key: str = ""
    agnes_base_url: str = "https://apihub.agnes-ai.com/v1"
    text_model: str = "flash"
    image_model: str = "agnes-image-v1"
    video_model: str = "agnes-video-v1"

    # Playwright
    playwright_browsers_path: int = 0

    # 加密
    encryption_key: str = "default-dev-key-change-in-production!!"

    # 服务器
    host: str = "0.0.0.0"
    port: int = 8765
    debug: bool = True

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"

    # Tauri
    tauri_dev_port: int = 1420


settings = Settings()
