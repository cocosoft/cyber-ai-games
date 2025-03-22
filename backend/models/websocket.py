"""WebSocket消息模型"""
from pydantic import BaseModel
from typing import Optional, Literal

class BaseWebSocketMessage(BaseModel):
    """WebSocket基础消息模型"""
    type: str
    version: str = "1.0"
    timestamp: Optional[float] = None

class GameMessage(BaseWebSocketMessage):
    """游戏相关消息模型"""
    game_id: str
    action: Literal["move", "status", "chat", "control"]
    data: dict

class SystemMessage(BaseWebSocketMessage):
    """系统消息模型"""
    action: Literal["ping", "pong", "error", "info"]
    message: Optional[str] = None

class ChatMessage(BaseWebSocketMessage):
    """聊天消息模型"""
    message: str
    sender: str
    recipient: Optional[str] = None
