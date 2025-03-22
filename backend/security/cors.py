"""CORS安全配置模块"""
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import os

def setup_cors(app, allowed_origins: List[str] = None):
    """配置CORS中间件
    
    Args:
        app: FastAPI应用实例
        allowed_origins: 允许的域名列表，如果为None则从环境变量读取
    """
    if allowed_origins is None:
        allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
        allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600
    )
