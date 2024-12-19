from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from app.db.session import get_db
from app.schemas.bracket import BracketCreate, Bracket, BracketUpdate
from app.schemas.user import User  # Добавляем импорт User
from app.core.security import get_current_user
from app.models.user import UserRole

router = APIRouter() 