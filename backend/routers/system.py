from fastapi import APIRouter, Depends, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..config_manager import ConfigManager
from ..database import get_db
from ..security import get_current_user
from ..models import User

router = APIRouter(prefix="/system", tags=["system"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/health")
@limiter.limit("10/second")
async def health_check(request):
    return {"status": "ok"}

@router.get("/config")
@limiter.limit("5/second")
async def get_config(
    request,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config_manager = ConfigManager(db)
    return config_manager.get_config()

@router.post("/config")
@limiter.limit("1/second")
async def update_config(
    request,
    config: dict,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    config_manager = ConfigManager(db)
    try:
        return config_manager.update_config(config)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/metrics")
@limiter.limit("5/second")
async def get_metrics(
    request,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # TODO: Implement metrics collection
    return {"metrics": {}}
