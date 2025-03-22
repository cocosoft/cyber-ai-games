from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel, validator
from typing import Dict, Any
import re

class SensitiveDataFilter:
    """敏感数据过滤器"""
    def __init__(self):
        self.sensitive_keys = ['password', 'token', 'secret', 'api_key']
        
    def filter_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """过滤字典中的敏感数据"""
        if not isinstance(data, dict):
            return data
            
        filtered = {}
        for key, value in data.items():
            if any(sensitive in key.lower() for sensitive in self.sensitive_keys):
                filtered[key] = "***FILTERED***"
            elif isinstance(value, dict):
                filtered[key] = self.filter_dict(value)
            elif isinstance(value, (list, tuple)):
                filtered[key] = [self.filter_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                filtered[key] = value
        return filtered

class SQLInjectionProtector:
    """SQL注入防护"""
    def __init__(self):
        self.sql_keywords = [
            'select', 'insert', 'update', 'delete', 'drop', 
            'truncate', 'create', 'alter', 'grant', 'revoke'
        ]
        self.sql_pattern = re.compile(
            r"([';]+|(--)+)", 
            re.IGNORECASE
        )
        
    def sanitize_input(self, data: Any) -> Any:
        """清理输入数据"""
        if isinstance(data, str):
            if self.sql_pattern.search(data):
                raise ValueError("Potential SQL injection detected")
            return data
        elif isinstance(data, dict):
            return {k: self.sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self.sanitize_input(item) for item in data]
        return data

def setup_cors(app: FastAPI):
    """配置CORS"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

def setup_rate_limit(app: FastAPI):
    """配置速率限制"""
    limiter = Limiter(key_func=get_remote_address)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

def setup_request_validation(app: FastAPI):
    """配置请求验证"""
    @app.middleware("http")
    async def validate_request(request: Request, call_next):
        # 检查请求头
        if not request.headers.get("Content-Type") == "application/json":
            raise HTTPException(
                status_code=400,
                detail="Invalid content type"
            )
            
        # 检查请求体大小
        if int(request.headers.get("Content-Length", 0)) > 1024 * 1024:  # 1MB
            raise HTTPException(
                status_code=413,
                detail="Request too large"
            )
            
        return await call_next(request)
