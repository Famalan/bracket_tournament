from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from app.models.tournament import TournamentStatus

class TournamentBase(BaseModel):
    name: str
    description: Optional[str] = None
    type: str
    rules: Optional[str] = None
    max_teams: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class TournamentCreate(TournamentBase):
    pass

class TournamentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    rules: Optional[str] = None
    max_teams: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[TournamentStatus] = None

class TournamentResponse(TournamentBase):
    id: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    status: TournamentStatus
    teams: List[dict] = []
    matches: List[dict] = []

    class Config:
        from_attributes = True 

class TournamentStatusUpdate(BaseModel):
    status: TournamentStatus