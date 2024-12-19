from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class BracketBase(BaseModel):
    tournament_id: int
    match_id: int
    round: int
    position: int

class BracketCreate(BracketBase):
    pass

class BracketUpdate(BaseModel):
    round: Optional[int] = None
    position: Optional[int] = None

class Bracket(BracketBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 