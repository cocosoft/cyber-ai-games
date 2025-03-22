from .base import BaseRouter
from .game import router as game_router
from .model import router as model_router
from .websocket import router as websocket_router
from .system import router as system_router

__all__ = [
    'BaseRouter',
    'game_router',
    'model_router', 
    'websocket_router',
    'system_router'
]
