import os
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from cryptography.fernet import Fernet
import logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from backend.logging_config import logger

# 配置加密密钥
CONFIG_KEY = os.getenv("CONFIG_KEY", Fernet.generate_key().decode())
fernet = Fernet(CONFIG_KEY.encode())

class ConfigChangeHandler(FileSystemEventHandler):
    """配置文件变更处理器"""
    def __init__(self, callback):
        self.callback = callback

    def on_modified(self, event):
        if event.src_path.endswith(".env"):
            self.callback()

class AppSettings(BaseSettings):
    """应用配置"""
    __slots__ = ()
    
    app_name: str = Field("Cyber AI Games", env="APP_NAME")
    app_version: str = Field("1.0.0", env="APP_VERSION")
    debug: bool = Field(False, env="DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    database_url: str = Field(..., env="DATABASE_URL")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    cors_origins: str = Field("*", env="CORS_ORIGINS")
    allowed_origins: str = Field("http://localhost:5174", env="ALLOWED_ORIGINS")
    rate_limit: int = Field(100, env="RATE_LIMIT")
    config_version: int = Field(1, env="CONFIG_VERSION")
    
    # 限流配置
    ratelimit_enabled: bool = Field(True, env="RATELIMIT_ENABLED")
    ratelimit_default: List[str] = Field(["100/minute"], env="RATELIMIT_DEFAULT", description="Default rate limits", json_schema_extra={"example": ["100/minute"]})
    ratelimit_storage_uri: str = Field("memory://", env="RATELIMIT_STORAGE_URI")
    
    # LLM API keys
    baichuan_api_key: str = Field(..., env="BAICHUAN_API_KEY")
    baichuan_base_url: str = Field(..., env="BAICHUAN_BASE_URL")
    baichuan_default_model: str = Field(..., env="BAICHUAN_DEFAULT_MODEL")
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    zhipuai_api_key: str = Field(..., env="ZHIPUAI_API_KEY")
    moonshot_api_key: str = Field(..., env="MOONSHOT_API_KEY")
    minimax_api_key: str = Field(..., env="MINIMAX_API_KEY")
    qwen_api_key: str = Field(..., env="QWEN_API_KEY")
    hunyuan_api_key: str = Field(..., env="HUNYUAN_API_KEY")
    zeroone_api_key: str = Field(..., env="ZEROONE_API_KEY")
    siliconflow_api_key: str = Field(..., env="SILICONFLOW_API_KEY")
    volcano_api_key: str = Field(..., env="VOLCANO_API_KEY")
    aihubmix_api_key: str = Field(..., env="AIHUBMIX_API_KEY")
    doubao_api_key: str = Field(..., env="DOUBAO_API_KEY")
    gemini_api_key: str = Field(..., env="GEMINI_API_KEY")
    deepseek_api_key: str = Field(..., env="DEEPSEEK_API_KEY")
    brain360_api_key: str = Field(..., env="BRAIN360_API_KEY")
    brain360_base_url: str = Field(..., env="BRAIN360_BASE_URL")
    brain360_default_model: str = Field(..., env="BRAIN360_DEFAULT_MODEL")
    sensechat_api_key: str = Field(..., env="SENSECHAT_API_KEY")
    sensechat_base_url: str = Field(..., env="SENSECHAT_BASE_URL")
    sensechat_default_model: str = Field(..., env="SENSECHAT_DEFAULT_MODEL")
    
    # Encryption settings
    encryption_key: str = Field(..., env="ENCRYPTION_KEY")
    
    # Server settings
    host: str = Field("127.0.0.1", env="HOST")
    port: int = Field(8000, env="PORT")

    @validator('database_url')
    def validate_db_url(cls, v):
        if not v.startswith(('postgresql://', 'sqlite://')):
            raise ValueError('Invalid database URL')
        return v

    @validator('log_level')
    def validate_log_level(cls, v):
        if v.upper() not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
            raise ValueError('Invalid log level')
        return v.upper()

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        secrets_dir = "/run/secrets"
        extra = "forbid"

# 初始化配置
settings = AppSettings()

# 配置热重载
def reload_config():
    """重新加载配置"""
    global settings
    settings = AppSettings()
    logger.info("Configuration reloaded")

# 启动配置监控
observer = Observer()
event_handler = ConfigChangeHandler(reload_config)
observer.schedule(event_handler, path=".", recursive=False)
observer.start()

# 加密敏感配置
def encrypt_config(value: str) -> str:
    """加密配置值"""
    return fernet.encrypt(value.encode()).decode()

def decrypt_config(value: str) -> str:
    """解密配置值"""
    return fernet.decrypt(value.encode()).decode()

# 初始化模板
templates = Jinja2Templates(directory="backend/templates")

from backend.game_manager import game_manager

def create_app() -> FastAPI:
    """创建FastAPI应用"""
    app = FastAPI(
        title=settings.app_name,
        description="API for AI-powered game platform",
        version=settings.app_version,
        debug=settings.debug,
    )

    # 初始化游戏管理器
    game_manager.initialize()
    logger.info("GameManager initialized successfully")

    # 挂载静态文件
    app.mount("/static", StaticFiles(directory="backend/static"), name="static")

    # 配置CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins.split(","),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 配置日志
    from backend.logging_config import set_log_level
    set_log_level(settings.log_level)

    @app.on_event("shutdown")
    def shutdown_event():
        """应用关闭时停止配置监控"""
        observer.stop()
        observer.join()

    return app
