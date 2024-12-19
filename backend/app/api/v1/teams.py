from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.schemas.team import TeamCreate, TeamResponse
from app.models.team import Team
from app.core.security import get_current_user
from app.models.user import User, UserRole
from typing import List
from sqlalchemy import select, delete, and_
from app.models.team_member import TeamMember
from app.schemas.user import UserResponse, UserBase
from pydantic import BaseModel
import logging
from datetime import datetime
from sqlalchemy.orm import selectinload

logger = logging.getLogger(__name__)

router = APIRouter()

class TeamMemberAdd(BaseModel):
    user_id: int

@router.get("/", response_model=List[TeamResponse])
async def get_teams(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Получаем команды вместе с участниками
        query = select(Team).options(
            selectinload(Team.members)
        )
        result = await db.execute(query)
        teams = result.scalars().all()
        
        return teams
    except Exception as e:
        logger.error(f"Error getting teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/", response_model=TeamResponse)
async def create_team(
    team: TeamCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    new_team = Team(**team.dict(), captain_id=current_user.id)
    session.add(new_team)
    await session.commit()
    await session.refresh(new_team)
    return new_team

@router.delete("/{team_id}")
async def delete_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admins can delete teams")
    
    team = await session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    await session.delete(team)
    await session.commit()
    return {"message": "Team deleted successfully"}

@router.get("/{team_id}/members", response_model=List[UserBase])
async def get_team_members(
    team_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Проверяем существование команды
        team = await session.get(Team, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        # Получаем участников команды
        query = select(User).join(TeamMember).where(TeamMember.team_id == team_id)
        result = await session.execute(query)
        members = result.scalars().all()

        # Преобразуем SQLAlchemy модели в Pydantic модели, исключая created_at и updated_at
        return [
            UserBase(
                id=member.id,
                username=member.username,
                email=member.email,
                role=member.role
            ) for member in members
        ]
    except Exception as e:
        logger.error(f"Error getting team members: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.post("/{team_id}/members", status_code=status.HTTP_201_CREATED)
async def add_team_member(
    team_id: int,
    member: TeamMemberAdd,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    try:
        # Проверяем существование команды
        team = await session.get(Team, team_id)
        if not team:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )
        
        # Прверяем права доступа
        if current_user.role != UserRole.ADMIN and team.captain_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only team captain or admin can add members"
            )
        
        # Проверяем, существует ли пользователь
        user = await session.get(User, member.user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Проверяем, не является ли пользователь уже членом команды
        query = select(TeamMember).where(
            and_(
                TeamMember.team_id == team_id,
                TeamMember.user_id == member.user_id
            )
        )
        result = await session.execute(query)
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a team member"
            )
        
        # Добавляем пользователя в команду
        team_member = TeamMember(team_id=team_id, user_id=member.user_id)
        session.add(team_member)
        await session.commit()
        
        return {"message": "User added to team successfully"}
    except Exception as e:
        logger.error(f"Error adding team member: {str(e)}")
        await session.rollback()  # Добавляем откат транзакции при ошибке
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: int,
    user_id: int,
    session: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Проверяем права доступа
    team = await session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER] and team.captain_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    # Удаляем участника
    query = delete(TeamMember).where(
        and_(
            TeamMember.team_id == team_id,
            TeamMember.user_id == user_id
        )
    )
    result = await session.execute(query)
    await session.commit()
    
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Member not found")
    
    return {"message": "Member removed successfully"}

@router.get("/my")
async def get_my_teams(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Получить команды текущего пользователя (где он капитан или участник)"""
    try:
        # Получаем команды, где пользователь является капитаном
        captain_query = select(Team).where(Team.captain_id == current_user.id)
        captain_result = await db.execute(captain_query)
        captain_teams = captain_result.scalars().all()

        # Получаем команды, где пользователь является участником
        member_query = (
            select(Team)
            .join(TeamMember)
            .where(TeamMember.user_id == current_user.id)
        )
        member_result = await db.execute(member_query)
        member_teams = member_result.scalars().all()

        # Объединяем результаты (убираем дубликаты)
        all_teams = list({team.id: team for team in captain_teams + member_teams}.values())

        return all_teams
    except Exception as e:
        logger.error(f"Error getting user teams: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user teams"
        )