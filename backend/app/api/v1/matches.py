from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from app.db.session import get_db
from app.schemas.match import MatchCreate, Match, MatchUpdate, MatchResult
from app.schemas.user import User
from app.core.security import get_current_user
from app.models.user import UserRole

router = APIRouter()

@router.get("/", response_model=List[Match])
async def get_matches(
    skip: int = 0,
    limit: int = 10,
    tournament_id: int = None,
    db: AsyncSession = Depends(get_db)
):
    """Получение списка матчей"""
    base_query = """
        SELECT 
            m.*,
            t.name as tournament_name,
            t1.name as team1_name,
            t2.name as team2_name,
            w.name as winner_name
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.id
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        LEFT JOIN teams w ON m.winner_id = w.id
    """
    
    if tournament_id:
        where_clause = "WHERE m.tournament_id = :tournament_id"
    else:
        where_clause = ""
    
    query = text(f"""
        {base_query}
        {where_clause}
        ORDER BY m.start_time DESC
        LIMIT :limit OFFSET :skip
    """)
    
    params = {"limit": limit, "skip": skip}
    if tournament_id:
        params["tournament_id"] = tournament_id
        
    result = await db.execute(query, params)
    return result.fetchall()

@router.post("/", response_model=Match)
async def create_match(
    match: MatchCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Создание нового матча (только для организаторов и админов)"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверяем, что команды участвуют в турнире
    query = text("""
        SELECT COUNT(*) 
        FROM tournament_teams 
        WHERE tournament_id = :tournament_id 
        AND team_id IN (:team1_id, :team2_id)
    """)
    
    result = await db.execute(
        query, 
        {
            "tournament_id": match.tournament_id,
            "team1_id": match.team1_id,
            "team2_id": match.team2_id
        }
    )
    
    if result.scalar() < 2:
        raise HTTPException(
            status_code=400, 
            detail="Обе команды должны быть зарегистрированы в турнире"
        )
    
    query = text("""
        INSERT INTO matches (
            tournament_id, team1_id, team2_id, 
            start_time, status
        )
        VALUES (
            :tournament_id, :team1_id, :team2_id, 
            :start_time, :status
        )
        RETURNING *
    """)
    
    try:
        result = await db.execute(
            query,
            {
                "tournament_id": match.tournament_id,
                "team1_id": match.team1_id,
                "team2_id": match.team2_id,
                "start_time": match.start_time,
                "status": "scheduled"
            }
        )
        await db.commit()
        return result.fetchone()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка создания матча")

@router.post("/{match_id}/result", response_model=Match)
async def update_match_result(
    match_id: int,
    result: MatchResult,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление результата матча"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
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
        result = await db.execute(
            query,
            {
                "match_id": match_id,
                "score_team1": result.score_team1,
                "score_team2": result.score_team2
            }
        )
        await db.commit()
        
        # Триггер update_match_statistics автоматически определит победителя
        return result.fetchone()
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка обновления результата")

@router.get("/{match_id}", response_model=Match)
async def get_match(match_id: int, db: AsyncSession = Depends(get_db)):
    """Получение информации о матче"""
    query = text("""
        SELECT 
            m.*,
            t.name as tournament_name,
            t1.name as team1_name,
            t2.name as team2_name,
            w.name as winner_name
        FROM matches m
        JOIN tournaments t ON m.tournament_id = t.id
        JOIN teams t1 ON m.team1_id = t1.id
        JOIN teams t2 ON m.team2_id = t2.id
        LEFT JOIN teams w ON m.winner_id = w.id
        WHERE m.id = :match_id
    """)
    
    result = await db.execute(query, {"match_id": match_id})
    match = result.fetchone()
    
    if not match:
        raise HTTPException(status_code=404, detail="Матч не найден")
    return match 