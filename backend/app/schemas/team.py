from pydantic import BaseModel
from app.schemas.user import UserResponse
from typing import Optional, List

class TeamBase(BaseModel):
    name: str
    description: str | None = None
    logo_url: str | None = None

class TeamCreate(TeamBase):
    pass

class TeamResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    captain_id: Optional[int] = None
    members: List[UserResponse]

    class Config:
        from_attributes = True 