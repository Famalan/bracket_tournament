from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class MatchStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class MatchBase(BaseModel):
    tournament_id: int
    team1_id: int
    team2_id: int
    start_time: datetime

class MatchCreate(MatchBase):
    pass

class MatchUpdate(BaseModel):
    """Схема для обновления матча"""
    start_time: Optional[datetime] = None
    status: Optional[MatchStatus] = None
    score_team1: Optional[int] = Field(None, ge=0)
    score_team2: Optional[int] = Field(None, ge=0)
    notes: Optional[str] = None

class MatchResult(BaseModel):
    """Схема для обновления результата матча"""
    score_team1: int = Field(..., ge=0)
    score_team2: int = Field(..., ge=0)

class Match(MatchBase):
    """Полная схема матча"""
    id: int
    status: MatchStatus
    score_team1: Optional[int] = None
    score_team2: Optional[int] = None
    winner_id: Optional[int] = None
    end_time: Optional[datetime] = None
    tournament_name: Optional[str] = None
    team1_name: Optional[str] = None
    team2_name: Optional[str] = None
    winner_name: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 