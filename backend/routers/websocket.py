from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import ValidationError

from ..game_manager import GameManager
from ..database import get_db
from ..security import get_current_user_ws, RequestValidator
from ..models import User

router = APIRouter(prefix="/ws", tags=["websocket"])
limiter = Limiter(key_func=get_remote_address)
validator = RequestValidator()

@router.websocket("/game/{game_id}")
async def websocket_game_endpoint(
    websocket: WebSocket,
    game_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user_ws)
):
    game_manager = GameManager(db)
    await websocket.accept()
    try:
        while True:
            raw_message = await websocket.receive_text()
            try:
                # 验证消息格式
                validated_data = validator.validate_websocket_message(
                    f"/ws/game/{game_id}", 
                    raw_message
                )
                # 处理已验证的消息
                response = game_manager.handle_websocket_message(
                    game_id, 
                    validated_data
                )
                await websocket.send_text(response)
            except ValidationError as e:
                await websocket.send_text(json.dumps({
                    "error": "validation_error",
                    "details": e.errors()
                }))
            except ValueError as e:
                await websocket.send_text(json.dumps({
                    "error": "invalid_message",
                    "details": str(e)
                }))
    except WebSocketDisconnect:
        game_manager.handle_disconnect(game_id)
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))

@router.websocket("/chat")
async def websocket_chat_endpoint(
    websocket: WebSocket,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user_ws)
):
    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            # Handle chat message
            await websocket.send_text(f"Message received: {message}")
    except WebSocketDisconnect:
        # Handle disconnect
        pass
    except Exception as e:
        await websocket.close(code=1011, reason=str(e))
