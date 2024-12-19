from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime

from app.models.user import UserRole
from app.schemas.tournament import TournamentCreate, Tournament, TournamentUpdate

class TournamentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_tournament(self, tournament: TournamentCreate, user_id: int) -> Tournament:
        """Создание нового турнира"""
        query = text("""
            INSERT INTO tournaments (
                name, description, type, status, rules, 
                max_teams, registration_deadline, start_date, 
                end_date, created_by
            )
            VALUES (
                :name, :description, :type, 'registration', :rules,
                :max_teams, :registration_deadline, :start_date,
                :end_date, :created_by
            )
            RETURNING *
        """)
        
        try:
            result = await self.db.execute(
                query,
                {
                    "name": tournament.name,
                    "description": tournament.description,
                    "type": tournament.type,
                    "rules": tournament.rules,
                    "max_teams": tournament.max_teams,
                    "registration_deadline": tournament.registration_deadline,
                    "start_date": tournament.start_date,
                    "end_date": tournament.end_date,
                    "created_by": user_id
                }
            )
            await self.db.commit()
            return result.fetchone()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def start_tournament(self, tournament_id: int) -> Tournament:
        """Запуск турнира и генерация сетки"""
        # Проверяем статус турнира
        query = text("""
            SELECT t.*, COUNT(tt.team_id) as team_count
            FROM tournaments t
            LEFT JOIN tournament_teams tt ON t.id = tt.tournament_id
            WHERE t.id = :tournament_id AND tt.status = 'accepted'
            GROUP BY t.id
        """)
        
        result = await self.db.execute(query, {"tournament_id": tournament_id})
        tournament = result.fetchone()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Турнир не найден")
            
        if tournament.status != 'registration':
            raise HTTPException(status_code=400, detail="Турнир уже запущен или завершен")
            
        if tournament.team_count < 2:
            raise HTTPException(status_code=400, detail="Недостаточно команд для начала турнира")

        # Вызываем процедуру генерации матчей
        query = text("CALL generate_tournament_matches(:tournament_id)")
        await self.db.execute(query, {"tournament_id": tournament_id})
        await self.db.commit()
        
        return tournament 