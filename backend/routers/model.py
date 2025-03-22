from fastapi import APIRouter, Depends, HTTPException, Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from ..llm_manager import LLMManager
from ..database import get_db
from ..security import get_current_user
from ..models import User

router = APIRouter(prefix="/models", tags=["models"])
limiter = Limiter(key_func=get_remote_address)

@router.get("/")
@limiter.limit("5/second")
async def list_models(
    request: Request,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    llm_manager = LLMManager(db)
    return llm_manager.list_models()

@router.post("/{model_id}/activate")
@limiter.limit("1/second")
async def activate_model(
    request: Request,
    model_id: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    llm_manager = LLMManager(db)
    try:
        return llm_manager.activate_model(model_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/inference")
@limiter.limit("10/second")
async def run_inference(
    request: Request,
    prompt: str,
    db=Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    llm_manager = LLMManager(db)
    try:
        return llm_manager.run_inference(prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
