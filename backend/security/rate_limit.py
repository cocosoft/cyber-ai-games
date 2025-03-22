"""请求速率限制和大小限制模块"""
import time
from fastapi import Request, HTTPException
from fastapi.middleware import Middleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from typing import Optional, Callable, Awaitable
import os
import time

class RateLimiter:
    """请求速率限制器"""
    
    def __init__(self, max_requests: int = 100, window: int = 60):
        """
        Args:
            max_requests: 每个时间窗口内允许的最大请求数
            window: 时间窗口长度（秒）
        """
        self.max_requests = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", max_requests))
        self.window = int(os.getenv("RATE_LIMIT_WINDOW", window))
        self.request_counts = {}

    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = int(time.time())
        
        # 清理过期记录
        self.request_counts = {
            ip: count 
            for ip, (timestamp, count) in self.request_counts.items()
            if current_time - timestamp < self.window
        }
        
        # 更新计数
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = (current_time, 1)
        else:
            timestamp, count = self.request_counts[client_ip]
            self.request_counts[client_ip] = (timestamp, count + 1)
        
        # 检查是否超过限制
        if self.request_counts[client_ip][1] > self.max_requests:
            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Limit is {self.max_requests} requests per {self.window} seconds"
            )

def setup_rate_limit(app, max_requests: Optional[int] = None, window: Optional[int] = None):
    """配置速率限制中间件
    
    Args:
        app: FastAPI应用实例
        max_requests: 每个时间窗口内允许的最大请求数
        window: 时间窗口长度（秒）
    """
    @app.middleware("http")
    async def rate_limit_middleware(request: Request, call_next):
        limiter = RateLimiter(max_requests=max_requests, window=window)
        return await limiter.dispatch(request, call_next)
    
    # 添加请求体大小限制
    app.add_middleware(GZipMiddleware)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    app.add_middleware(HTTPSRedirectMiddleware)
