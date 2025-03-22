from fastapi import APIRouter, Depends, Request, status, WebSocket, Security
from .routers import game, model, websocket, system
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
from typing import Dict, Optional, List
from datetime import datetime
import logging
from slowapi import Limiter
from slowapi.util import get_remote_address
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.security.authentication import auth_scheme, get_current_user
from backend.app_config import templates
from backend.game_manager import GameManager

game_manager = GameManager()
from backend.game_engine.js_red_alert_engine import JSRedAlertEngine
from backend.llm_manager import LLMManager
llm_manager = LLMManager()
from backend.config_manager import save_config, get_config
from backend.database import get_db
from backend.logging_config import logger
from backend.exceptions import (
    ValidationError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    ServiceUnavailableError
)

from slowapi.util import get_remote_address
from slowapi.extension import Limiter as BaseLimiter
from typing import Callable, Optional, List

class CustomLimiter(BaseLimiter):
    def __init__(
        self,
        key_func: Callable,
        default_limits: Optional[List[str]] = None,
        **kwargs
    ):
        # Initialize parent class with minimal required attributes
        super().__init__(key_func=key_func)
        # Store key_func as both key_func and _key_func for compatibility
        self.key_func = key_func
        self._key_func = key_func
        self.default_limits = default_limits or []
        # Store additional configuration
        self._storage = kwargs.get('storage')
        self._headers_enabled = kwargs.get('headers_enabled', True)
        self._retry_after = kwargs.get('retry_after', 'http-date')
        self._strategy = kwargs.get('strategy', 'fixed-window')
        self._auto_check = kwargs.get('auto_check', False)

# 创建自定义限流器实例
limiter = CustomLimiter(
    key_func=get_remote_address,
    default_limits=["100 per minute"]
)

# API版本
API_VERSION = "v1"

router = APIRouter(
    prefix=f"/api/{API_VERSION}",
    tags=["api"],
    responses={
        status.HTTP_400_BAD_REQUEST: {"description": "Invalid request"},
        status.HTTP_401_UNAUTHORIZED: {"description": "Unauthorized"},
        status.HTTP_404_NOT_FOUND: {"description": "Not found"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Internal server error"},
    }
)

# Include all routers
router.include_router(game.router)
router.include_router(model.router)
router.include_router(websocket.router)
router.include_router(system.router)

# 添加根路径路由
@router.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Cyber AI Games</title>
        </head>
        <body>
            <h1>Welcome to Cyber AI Games API</h1>
            <p>API documentation available at <a href="/api/docs">/api/docs</a></p>
        </body>
    </html>
    """

@router.websocket("/play")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        try:
            data = await websocket.receive_json()
            
            # 处理开始游戏请求
            if data.get("type") == "start_game":
                await websocket.send_json({
                    "type": "game_started",
                    "message": "Game started successfully"
                })
                continue
                
            # 处理游戏状态更新
            if data.get("type") == "state_update":
                game_type = data.get("game_type")
                engine = game_manager.get_game_engine(game_type)
                
                # 特殊处理JS红警游戏状态
                if game_type == "js_red_alert":
                    state = engine.game_state
                else:
                    state = engine.get_state()
                    
                await websocket.send_json({
                    "type": "state_update",
                    "state": state
                })
            
            # 处理聊天消息
            elif data.get("type") == "chat_message":
                message = data.get("message")
                # 调用LLM生成回复
                llm = llm_manager.get_llm_proxy()
                response = llm.generate_response(message)
                await websocket.send_json({
                    "type": "chat_message",
                    "message": response
                })
            
            # 处理玩家加入
            elif data.get("type") == "join_game":
                game_type = data.get("game_type")
                player_id = data.get("player_id")
                engine = game_manager.get_game_engine(game_type)
                success = engine.add_player(player_id)
                await websocket.send_json({
                    "type": "join_result",
                    "success": success,
                    "player_id": player_id
                })
                
            # 处理游戏动作
            elif data.get("type") == "game_action":
                game_type = data.get("game_type")
                action = data.get("action")
                engine = game_manager.get_game_engine(game_type)
                
                try:
                    # JSRedAlert特殊处理
                    if game_type == "js_red_alert":
                        player_id = data.get("player_id")
                        if not player_id:
                            raise ValidationError("Missing player_id in action data")
                            
                        result = engine.handle_action(player_id, action)
                        await websocket.send_json({
                            "type": "game_action_result",
                            "result": result,
                            "state": engine.get_state(),
                            "player_id": player_id
                        })
                    else:
                        player_id = data.get("player_id")
                        result = engine.handle_action(player_id, action)
                        await websocket.send_json({
                            "type": "game_action_result",
                            "result": result,
                            "state": engine.get_state()
                        })
                except Exception as e:
                    logger.error(f"处理游戏动作失败: {str(e)}")
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e)
                    })
                    
        except Exception as e:
            logger.error(f"WebSocket error: {str(e)}")
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })

# 请求模型定义
class ModelConfig(BaseModel):
    api_key: str = Field(..., min_length=32, max_length=128)
    endpoint: Optional[str] = Field(None, max_length=256)
    enabled: bool = Field(default=False)
    priority: int = Field(default=1, ge=1, le=10)

    @validator('endpoint')
    def validate_endpoint(cls, v):
        if v and not v.startswith(('http://', 'https://')):
            raise ValidationError('Endpoint must start with http:// or https://')
        return v

class ModelStatusResponse(BaseModel):
    name: str
    enabled: bool
    config: ModelConfig

class GameMoveRequest(BaseModel):
    move: str = Field(..., min_length=1, max_length=256)
    player: str = Field(..., min_length=1, max_length=64)

# 带重试机制的请求处理
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=1, max=5),
    before_sleep=lambda retry_state: logger.warning(
        f"Retrying request (attempt {retry_state.attempt_number})..."
    )
)
async def process_request(request: Request):
    """记录请求日志"""
    logger.info(f"Request: {request.method} {request.url} from {request.client.host}")
    return {
        "timestamp": datetime.now().isoformat(),
        "method": request.method,
        "url": str(request.url),
        "client": request.client.host
    }

@router.get("/config", response_class=JSONResponse)
@limiter.limit("10/minute")
async def config_page(request: Request):
    """配置页面"""
    await process_request(request)
    return templates.TemplateResponse("config.html", {"request": request})

@router.get("/status", response_class=JSONResponse)
@limiter.limit("10/minute")
async def status_page(request: Request):
    """服务器状态页面"""
    await process_request(request)
    return {
        "status": "running",
        "last_updated": datetime.now().isoformat(),
        "system_status": {
            "uptime": "0 days 0 hours 0 minutes",
            "cpu_usage": "0%",
            "memory_usage": "0MB/0MB"
        },
        "model_status": "loading...",
        "service_status": {
            "api": "checking...",
            "database": "checking..."
        }
    }

@router.get("/models/status", response_model=List[ModelStatusResponse])
@limiter.limit("30/minute")
async def get_models_status(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    current_user: dict = Depends(get_current_user)
):
    """获取所有模型状态"""
    try:
        if current_user.get("role") != "admin":
            raise PermissionError("Insufficient permissions")
            
        await process_request(request)
        status = llm_manager.get_model_status()
        return [
            ModelStatusResponse(
                name=s.name,
                enabled=s.enabled,
                config=ModelConfig(
                    api_key=s.config.get('api_key', ''),
                    endpoint=s.config.get('endpoint'),
                    enabled=s.enabled
                )
            )
            for s in status
        ]
    except Exception as e:
        logger.error(f"获取模型状态失败: {str(e)}")
        raise ServiceUnavailableError("获取模型状态失败")

@router.post("/models", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def add_new_model(
    request: Request,
    model_name: str,
    config: ModelConfig,
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    current_user: dict = Depends(get_current_user)
):
    """添加新模型"""
    try:
        if current_user.get("role") != "admin":
            raise PermissionError("Insufficient permissions")
            
        await process_request(request)
        config_dict = config.dict()
        if llm_manager.add_model(model_name, config_dict):
            return {"message": f"Model {model_name} added successfully"}
        raise ValidationError(f"Failed to add model {model_name}")
    except Exception as e:
        logger.error(f"添加模型失败: {str(e)}")
        raise ServiceUnavailableError(str(e))

@router.delete("/models/{model_name}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def remove_model(
    request: Request,
    model_name: str,
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    current_user: dict = Depends(get_current_user)
):
    """删除模型"""
    try:
        if current_user.get("role") != "admin":
            raise PermissionError("Insufficient permissions")
            
        await process_request(request)
        if llm_manager.remove_model(model_name):
            return {"message": f"Model {model_name} removed successfully"}
        raise ValidationError(f"Failed to remove model {model_name}")
    except Exception as e:
        logger.error(f"删除模型失败: {str(e)}")
        raise ServiceUnavailableError(str(e))

@router.post("/models/{model_name}/enable", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def enable_model_endpoint(
    request: Request,
    model_name: str,
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    current_user: dict = Depends(get_current_user)
):
    """启用模型"""
    try:
        if current_user.get("role") != "admin":
            raise PermissionError("Insufficient permissions")
            
        await process_request(request)
        if llm_manager.enable_model(model_name):
            return {"message": f"Model {model_name} enabled successfully"}
        raise ValidationError(f"Failed to enable model {model_name}")
    except Exception as e:
        logger.error(f"启用模型失败: {str(e)}")
        raise ServiceUnavailableError(str(e))

@router.post("/models/{model_name}/disable", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def disable_model_endpoint(
    request: Request,
    model_name: str,
    credentials: HTTPAuthorizationCredentials = Security(auth_scheme),
    current_user: dict = Depends(get_current_user)
):
    """禁用模型"""
    try:
        if current_user.get("role") != "admin":
            raise PermissionError("Insufficient permissions")
            
        await process_request(request)
        if llm_manager.disable_model(model_name):
            return {"message": f"Model {model_name} disabled successfully"}
        raise ValidationError(f"Failed to disable model {model_name}")
    except Exception as e:
        logger.error(f"禁用模型失败: {str(e)}")
        raise ServiceUnavailableError(str(e))

@router.get("/games/{game_type}", response_model=Dict)
@limiter.limit("30/minute")
async def get_game_state(request: Request, game_type: str):
    """获取游戏状态"""
    try:
        await process_request(request)
        engine = game_manager.get_game_engine(game_type)
        return {"state": engine.get_state()}
    except ValueError as e:
        raise ValidationError(str(e))

@router.post("/games/{game_type}/move", response_model=Dict)
@limiter.limit("10/minute")
async def make_move(
    request: Request,
    game_type: str,
    move_data: GameMoveRequest
):
    """执行游戏移动"""
    try:
        await process_request(request)
        engine = game_manager.get_game_engine(game_type)
        result = engine.make_move(move_data.move, move_data.player)
        return {"result": result}
    except ValueError as e:
        raise ValidationError(str(e))
