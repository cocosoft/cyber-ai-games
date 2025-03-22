from functools import wraps
from fastapi import Request
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from backend.logging_config import logger

def validate_json_middleware(app):
    """
    验证请求体是否为有效JSON的中间件

    此中间件用于包裹应用程序，以确保所有传入的HTTP请求体都是有效的JSON格式
    如果请求不是HTTP类型或请求体不是有效的JSON，则返回400错误码和错误信息

    参数:
    - app: 被包装的应用程序

    返回:
    - middleware: 实际执行的中间件函数
    """
    # 使用wraps装饰器包装原始应用，以保持其元数据
    @wraps(app)
    async def middleware(scope, receive, send):
        # 检查当前scope是否为HTTP类型，非HTTP请求直接传递给原始应用
        if scope['type'] != 'http':
            return await app(scope, receive, send)
            
        # 创建Request对象，用于处理HTTP请求
        request = Request(scope, receive)
        try:
            # 尝试获取请求体，如果请求体为空，则不做任何处理
            body = await request.body()
            if body:
                # 如果请求体不为空，尝试解析为JSON
                await request.json()
        except ValueError:
            # 如果解析JSON时出现ValueError，表示请求体不是有效的JSON
            # 返回400错误码和错误信息
            response = JSONResponse(
                status_code=400,
                content={"message": "Invalid JSON"}
            )
            return await response(scope, receive, send)
            
        # 如果请求体为空或成功解析为JSON，则继续传递请求给原始应用
        return await app(scope, receive, send)
    # 返回中间件函数
    return middleware

def log_requests_middleware(app):
    """
    记录请求日志的中间件。
    
    该中间件包裹一个应用程序，并在处理每个HTTP请求时记录日志。
    它记录了请求的方法和URL，以及请求处理的结果状态码或错误信息。
    
    参数:
    - app: 被包裹的应用程序。
    
    返回:
    - 一个中间件函数，它将处理传入的请求并在传递给原始应用程序之前记录请求信息。
    """
    # 使用wraps装饰器来复制原始应用程序的元数据，如名称和文档字符串
    @wraps(app)
    async def middleware(scope, receive, send):
        # 如果请求类型不是HTTP，则直接传递给应用程序，不进行日志记录
        if scope['type'] != 'http':
            return await app(scope, receive, send)
            
        # 创建一个Request对象，以便于访问请求信息
        request = Request(scope, receive)
        # 记录请求的方法和URL
        logger.info(f"Incoming request: {request.method} {request.url}")
        try:
            # 调用原始应用程序并捕获响应
            response = await app(scope, receive, send)
            # 如果有响应，则记录响应的状态码
            if response:
                logger.info(f"Request completed: {response.status_code}")
            return response
        except Exception as e:
            # 如果在处理请求时发生异常，记录错误信息并重新抛出异常
            logger.error(f"Request failed: {str(e)}")
            raise
    return middleware

from backend.security.authentication import auth_scheme

def create_middleware_stack(app):
    """
    创建中间件栈

    该函数接收一个应用程序实例，并为其添加多个中间件以处理各种功能
    中间件按照添加的顺序形成一个栈，处理请求时从上到下，响应时从下到上

    参数:
    app: 应用程序实例，通常是一个Web框架的实例

    返回:
    app: 添加了中间件的应用程序实例
    """
    # 添加验证JSON的中间件，确保传入的JSON数据格式正确
    app.add_middleware(validate_json_middleware)
    # 添加记录请求日志的中间件，用于监控和调试
    app.add_middleware(log_requests_middleware)
    # 添加JWT认证中间件
    app.add_middleware(auth_scheme)
    # 添加信任主机中间件，允许所有主机访问（通配符"*"）
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
    # 添加GZip中间件，压缩响应数据，提高网络传输效率
    app.add_middleware(GZipMiddleware)
    # 暂时禁用HTTPS重定向中间件
    # app.add_middleware(HTTPSRedirectMiddleware)
    return app

# 导出middleware
middleware = create_middleware_stack
