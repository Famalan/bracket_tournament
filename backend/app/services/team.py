from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from typing import List, Optional

from app.schemas.team import TeamCreate, Team, TeamUpdate

class TeamService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_for_tournament(
        self, team_id: int, tournament_id: int, user_id: int
    ) -> dict:
        """Регистрация команды на турнир"""
        # Проверяем права доступа
        query = text("""
            SELECT captain_id FROM teams WHERE id = :team_id
        """)
        result = await self.db.execute(query, {"team_id": team_id})
        team = result.fetchone()
        
        if not team or team.captain_id != user_id:
            raise HTTPException(
                status_code=403,
                detail="Только капитан может зарегистрировать команду"
            )

        # Проверяем возможность регистрации через функцию
        query = text("""
            SELECT check_tournament_registration(:tournament_id, :team_id) as can_register
        """)
        result = await self.db.execute(
            query, 
            {"tournament_id": tournament_id, "team_id": team_id}
        )
        
        if not result.scalar():
            raise HTTPException(
                status_code=400,
                detail="Регистрация на турнир невозможна"
            )

        # Регистрируем команду
        query = text("""
            INSERT INTO tournament_teams (tournament_id, team_id, status)
            VALUES (:tournament_id, :team_id, 'pending')
            RETURNING *
        """)
        
        try:
            result = await self.db.execute(
                query,
                {"tournament_id": tournament_id, "team_id": team_id}
            )
            await self.db.commit()
            return result.fetchone()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e)) 