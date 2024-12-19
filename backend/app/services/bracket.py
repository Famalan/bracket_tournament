from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from typing import List, Dict

class BracketService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_tournament_bracket(self, tournament_id: int) -> List[Dict]:
        """Получение турнирной сетки"""
        query = text("""
            WITH RECURSIVE bracket_tree AS (
                -- Первый раунд (корневые матчи)
                SELECT 
                    b.tournament_id,
                    b.match_id,
                    b.round,
                    b.position,
                    b.next_match_id,
                    m.team1_id,
                    m.team2_id,
                    m.score_team1,
                    m.score_team2,
                    m.winner_id,
                    m.status,
                    1 as level
                FROM bracket b
                JOIN matches m ON b.match_id = m.id
                WHERE b.tournament_id = :tournament_id 
                AND b.round = 1

                UNION ALL

                -- Рекурсивно получаем следующие матчи
                SELECT 
                    b.tournament_id,
                    b.match_id,
                    b.round,
                    b.position,
                    b.next_match_id,
                    m.team1_id,
                    m.team2_id,
                    m.score_team1,
                    m.score_team2,
                    m.winner_id,
                    m.status,
                    bt.level + 1
                FROM bracket b
                JOIN matches m ON b.match_id = m.id
                JOIN bracket_tree bt ON b.match_id = bt.next_match_id
            )
            SELECT 
                bt.*,
                t1.name as team1_name,
                t2.name as team2_name,
                w.name as winner_name
            FROM bracket_tree bt
            LEFT JOIN teams t1 ON bt.team1_id = t1.id
            LEFT JOIN teams t2 ON bt.team2_id = t2.id
            LEFT JOIN teams w ON bt.winner_id = w.id
            ORDER BY bt.round, bt.position
        """)
        
        result = await self.db.execute(query, {"tournament_id": tournament_id})
        bracket = result.fetchall()
        
        if not bracket:
            raise HTTPException(status_code=404, detail="Турнирная сетка не найд��на")
            
        return bracket 