"""请求验证模块"""
from fastapi import Request, HTTPException
from pydantic import BaseModel, ValidationError
from typing import Any, Dict, Optional, Type
import json

class RequestValidator:
    """请求验证器"""
    
    def __init__(self):
        self.validators = {}

    def register_validator(self, endpoint: str, model: Type[BaseModel]):
        """注册请求验证器
        
        Args:
            endpoint: 需要验证的端点路径
            model: 用于验证的Pydantic模型
        """
        self.validators[endpoint] = model

    async def validate_request(self, request: Request) -> Dict[str, Any]:
        """验证HTTP请求
        
        Args:
            request: FastAPI请求对象
            
        Returns:
            验证后的请求数据
            
        Raises:
            HTTPException: 如果验证失败
        """
        endpoint = request.url.path
        validator = self.validators.get(endpoint)
        
        if validator is None:
            return {}
            
        try:
            body = await request.body()
            if body:
                data = await request.json()
                return validator(**data).dict()
            return {}
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON format")
        except ValidationError as e:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "Validation error",
                    "errors": e.errors()
                }
            )

    def validate_websocket_message(self, endpoint: str, message: str) -> Dict[str, Any]:
        """验证WebSocket消息
        
        Args:
            endpoint: WebSocket端点路径
            message: 接收到的WebSocket消息
            
        Returns:
            验证后的消息数据
            
        Raises:
            ValueError: 如果消息格式无效
            ValidationError: 如果验证失败
        """
        validator = self.validators.get(endpoint)
        
        if validator is None:
            return {}
            
        try:
            data = json.loads(message)
            return validator(**data).dict()
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format")
        except ValidationError as e:
            raise ValidationError(
                errors=e.errors(),
                model=validator
            )

from ..models.websocket import GameMessage, SystemMessage, ChatMessage

def setup_request_validation(app):
    """配置请求验证中间件
    
    Args:
        app: FastAPI应用实例
    """
    validator = RequestValidator()
    
    # 注册WebSocket消息验证器
    validator.register_validator("/ws/game/{game_id}", GameMessage)
    validator.register_validator("/ws/chat", ChatMessage)
    
    @app.middleware("http")
    async def validation_middleware(request: Request, call_next):
        try:
            validated_data = await validator.validate_request(request)
            request.state.validated_data = validated_data
            return await call_next(request)
        except HTTPException as e:
            return e
