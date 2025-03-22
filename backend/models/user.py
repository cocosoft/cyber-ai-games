from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    disabled: bool = False
    roles: list[str] = []
