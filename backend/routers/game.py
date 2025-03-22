from fastapi import Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import Optional

from ..app_config import settings
from ..game_manager import GameManager
from ..database import get_db
from ..security import get_current_user
from ..models import User
from .base import BaseRouter
from ..exceptions import (
    ValidationError,
    NotFoundError,
    PermissionError
)

router = BaseRouter(prefix="/games", tags=["games"])
limiter = Limiter(key_func=get_remote_address, default_limits=settings.ratelimit_default)

@router.get("/")
@limiter.limit("5/second")
async def list_games(
    request: Request,
    game_type: Optional[str] = None,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        game_manager = GameManager(db)
        return game_manager.list_games(game_type)
    except ValidationError as e:
        raise ValidationError(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/")
@limiter.limit("2/second")
async def create_game(
    request: Request,
    game_type: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        game_manager = GameManager(db)
        return game_manager.create_game(game_type, current_user.id)
    except ValidationError as e:
        raise ValidationError(str(e))
    except PermissionError as e:
        raise PermissionError(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/{game_id}")
@limiter.limit("5/second")
async def get_game_state(
    request: Request,
    game_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        game_manager = GameManager(db)
        return game_manager.get_game_state(game_id)
    except NotFoundError as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
