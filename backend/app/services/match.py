from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from typing import List, Optional
from datetime import datetime

from app.schemas.match import MatchResult, Match

class MatchService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def update_match_result(
        self, match_id: int, result: MatchResult, user_id: int
    ) -> Match:
        """Обновление результата матча"""
        # Проверяем существование матча
        query = text("""
            SELECT m.*, t.created_by
            FROM matches m
            JOIN tournaments t ON m.tournament_id = t.id
            WHERE m.id = :match_id
        """)
        
        match = await self.db.execute(query, {"match_id": match_id})
        match_data = match.fetchone()
        
        if not match_data:
            raise HTTPException(status_code=404, detail="Матч не найден")
            
        if match_data.status == 'completed':
            raise HTTPException(status_code=400, detail="Результат ма��ча уже внесен")

        # Обновляем результат
        query = text("""
            UPDATE matches
            SET 
                score_team1 = :score_team1,
                score_team2 = :score_team2,
                status = 'completed',
                end_time = CURRENT_TIMESTAMP
            WHERE id = :match_id
            RETURNING *
        """)
        
        try:
            result = await self.db.execute(
                query,
                {
                    "match_id": match_id,
                    "score_team1": result.score_team1,
                    "score_team2": result.score_team2
                }
            )
            await self.db.commit()
            return result.fetchone()
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e)) 