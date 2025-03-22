from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class BaseAPIException(Exception):
    """基础API异常类"""
    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    detail: str = "Internal server error"
    
    def __init__(self, detail: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        self.detail = detail or self.detail
        self.context = context or {}
        super().__init__(self.detail)

class ValidationError(BaseAPIException):
    """请求验证错误"""
    status_code = status.HTTP_400_BAD_REQUEST
    detail = "Invalid request data"

class AuthenticationError(BaseAPIException):
    """认证错误"""
    status_code = status.HTTP_401_UNAUTHORIZED
    detail = "Authentication failed"

class PermissionError(BaseAPIException):
    """权限错误"""
    status_code = status.HTTP_403_FORBIDDEN
    detail = "Permission denied"

class NotFoundError(BaseAPIException):
    """资源未找到错误"""
    status_code = status.HTTP_404_NOT_FOUND
    detail = "Resource not found"

class RateLimitError(BaseAPIException):
    """速率限制错误"""
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    detail = "Too many requests"

class ServiceUnavailableError(BaseAPIException):
    """服务不可用错误"""
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    detail = "Service unavailable"

def handle_exception(request, exc: Exception):
    """全局异常处理"""
    if isinstance(exc, BaseAPIException):
        status_code = exc.status_code
        detail = exc.detail
    elif isinstance(exc, HTTPException):
        status_code = exc.status_code
        detail = exc.detail
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        detail = "Internal server error"
    
    # 记录错误日志
    logger.error(f"Error occurred: {str(exc)}", extra={
        "status_code": status_code,
        "detail": detail,
        "path": request.url.path,
        "method": request.method,
        "client": request.client.host if request.client else None
    })
    
    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": status_code,
                "message": detail,
                "path": request.url.path,
                "method": request.method
            }
        }
    )
