from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from typing import List
from app.schemas.tournament import TournamentResponse, TournamentCreate, TournamentStatusUpdate
from app.models.tournament import Tournament, TournamentStatus
from app.models.user import User, UserRole
from app.core.security import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/", response_model=List[TournamentResponse])
async def get_tournaments(db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT 
                t.id,
                t.name,
                t.type,
                t.description,
                t.rules,
                t.max_teams,
                t.start_date,
                t.end_date,
                t.created_by,
                t.created_at,
                t.updated_at,
                COALESCE(t.status, 'DRAFT') as status
            FROM tournaments t
            ORDER BY t.created_at DESC
        """)
        
        result = await db.execute(query)
        tournaments = result.fetchall()
        
        return [
            {
                "id": t.id,
                "name": t.name,
                "type": t.type,
                "description": t.description,
                "rules": t.rules,
                "max_teams": t.max_teams,
                "start_date": t.start_date,
                "end_date": t.end_date,
                "created_by": t.created_by,
                "created_at": t.created_at,
                "updated_at": t.updated_at,
                "status": TournamentStatus(t.status or "draft"),
                "teams": [],
                "matches": []
            }
            for t in tournaments
        ]
    except Exception as e:
        logger.error(f"Error getting tournaments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/", response_model=TournamentResponse)
async def create_tournament(
    tournament: TournamentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        query = text("""
            INSERT INTO tournaments (
                name,
                type,
                description,
                rules,
                max_teams,
                start_date,
                end_date,
                created_by,
                created_at,
                updated_at,
                status
            ) VALUES (
                :name,
                :type,
                :description,
                :rules,
                :max_teams,
                :start_date,
                :end_date,
                :created_by,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP,
                :status
            ) RETURNING *
        """)
        
        values = {
            "name": tournament.name,
            "type": tournament.type,
            "description": tournament.description,
            "rules": tournament.rules,
            "max_teams": tournament.max_teams,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
            "created_by": current_user.id,
            "status": TournamentStatus.DRAFT.value
        }
        
        result = await db.execute(query, values)
        await db.commit()
        
        created_tournament = result.fetchone()
        
        return {
            "id": created_tournament.id,
            "name": created_tournament.name,
            "type": created_tournament.type,
            "description": created_tournament.description,
            "rules": created_tournament.rules,
            "max_teams": created_tournament.max_teams,
            "start_date": created_tournament.start_date,
            "end_date": created_tournament.end_date,
            "created_by": created_tournament.created_by,
            "created_at": created_tournament.created_at,
            "updated_at": created_tournament.updated_at,
            "status": TournamentStatus(created_tournament.status),
            "teams": [],
            "matches": []
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{tournament_id}", response_model=TournamentResponse)
async def get_tournament(tournament_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("""
            SELECT 
                t.id,
                t.name,
                t.type,
                t.description,
                t.rules,
                t.max_teams,
                t.start_date,
                t.end_date,
                t.created_by,
                t.created_at,
                t.updated_at,
                COALESCE(t.status, 'DRAFT') as status,
                (
                    SELECT json_agg(json_build_object(
                        'id', teams.id,
                        'name', teams.name,
                        'members', (
                            SELECT json_agg(json_build_object(
                                'id', users.id,
                                'username', users.username
                            ))
                            FROM users
                            JOIN team_members ON users.id = team_members.user_id
                            WHERE team_members.team_id = teams.id
                        )
                    ))
                    FROM teams
                    JOIN tournament_teams ON teams.id = tournament_teams.team_id
                    WHERE tournament_teams.tournament_id = t.id
                ) as teams
            FROM tournaments t
            WHERE t.id = :tournament_id
        """)
        
        result = await db.execute(query, {"tournament_id": tournament_id})
        tournament = result.fetchone()
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Турнир не найден")
            
        return {
            "id": tournament.id,
            "name": tournament.name,
            "type": tournament.type,
            "description": tournament.description,
            "rules": tournament.rules,
            "max_teams": tournament.max_teams,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
            "created_by": tournament.created_by,
            "created_at": tournament.created_at,
            "updated_at": tournament.updated_at,
            "status": TournamentStatus(tournament.status),
            "teams": tournament.teams or [],
            "matches": []
        }
    except Exception as e:
        logger.error(f"Error getting tournament: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{tournament_id}", response_model=TournamentResponse)
async def update_tournament(
    tournament_id: int, 
    tournament: TournamentCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        # Сначала проверяем существование турнира
        check_query = text("SELECT id FROM tournaments WHERE id = :tournament_id")
        result = await db.execute(check_query, {"tournament_id": tournament_id})
        if not result.scalar():
            raise HTTPException(status_code=404, detail="Турнир не найден")

        query = text("""
            UPDATE tournaments 
            SET 
                name = :name,
                type = :type,
                description = :description,
                rules = :rules,
                max_teams = :max_teams,
                start_date = :start_date,
                end_date = :end_date,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = :tournament_id
            RETURNING 
                id,
                name,
                type,
                description,
                rules,
                max_teams,
                start_date,
                end_date,
                created_by,
                created_at,
                updated_at
        """)
        
        values = {
            "tournament_id": tournament_id,
            "name": tournament.name,
            "type": tournament.type,
            "description": tournament.description,
            "rules": tournament.rules,
            "max_teams": tournament.max_teams,
            "start_date": tournament.start_date,
            "end_date": tournament.end_date,
        }
        
        result = await db.execute(query, values)
        await db.commit()
        
        updated_tournament = result.fetchone()
        
        return {
            "id": updated_tournament.id,
            "name": updated_tournament.name,
            "type": updated_tournament.type,
            "description": updated_tournament.description,
            "rules": updated_tournament.rules,
            "max_teams": updated_tournament.max_teams,
            "start_date": updated_tournament.start_date,
            "end_date": updated_tournament.end_date,
            "created_by": updated_tournament.created_by,
            "created_at": updated_tournament.created_at,
            "updated_at": updated_tournament.updated_at
        }
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{tournament_id}")
async def delete_tournament(tournament_id: int, db: AsyncSession = Depends(get_db)):
    try:
        query = text("DELETE FROM tournaments WHERE id = :tournament_id")
        result = await db.execute(query, {"tournament_id": tournament_id})
        await db.commit()
        
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Турнир не найден")
            
        return {"message": "Турнир успешно удален"}
        
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{tournament_id}/status")
async def update_tournament_status(
    tournament_id: int,
    status_update: TournamentStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Обновить статус турнира"""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORGANIZER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and organizers can update tournament status"
        )

    tournament = await db.get(Tournament, tournament_id)
    if not tournament:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tournament not found"
        )

    # Проверяем валидность перехода статуса
    if tournament.status == TournamentStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change status of completed tournament"
        )

    # Разрешенные переходы статусов
    allowed_transitions = {
        TournamentStatus.DRAFT: [TournamentStatus.REGISTRATION],
        TournamentStatus.REGISTRATION: [TournamentStatus.IN_PROGRESS],
        TournamentStatus.IN_PROGRESS: [TournamentStatus.COMPLETED],
    }

    new_status = status_update.status
    if new_status not in allowed_transitions.get(tournament.status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change status from {tournament.status} to {new_status}"
        )

    tournament.status = new_status
    await db.commit()
    await db.refresh(tournament)

    return tournament

@router.post("/{tournament_id}/join")
async def join_tournament(
    tournament_id: int,
    team_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        team_id = team_data.get("team_id")
        if not team_id:
            raise HTTPException(status_code=400, detail="Team ID is required")

        # Проверяем существование турнира и его статус
        tournament = await db.execute(
            text("""
                SELECT t.*, 
                       (SELECT COUNT(*) FROM tournament_teams WHERE tournament_id = t.id) as current_teams
                FROM tournaments t
                WHERE t.id = :id
            """),
            {"id": tournament_id}
        )
        tournament = tournament.fetchone()
        
        logger.info(f"Tournament data: {tournament}")
        
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")

        if tournament.status != "REGISTRATION":
            raise HTTPException(
                status_code=400,
                detail="Tournament is not in registration phase"
            )

        if tournament.max_teams and tournament.current_teams >= tournament.max_teams:
            raise HTTPException(
                status_code=400,
                detail="Tournament has reached maximum number of teams"
            )

        # Проверяем существование команды и права пользователя
        team = await db.execute(
            text("""
                SELECT t.*, 
                       CASE 
                           WHEN t.captain_id = :user_id THEN true
                           WHEN EXISTS (
                               SELECT 1 FROM team_members 
                               WHERE team_id = t.id AND user_id = :user_id
                           ) THEN true
                           ELSE false
                       END as is_member
                FROM teams t
                WHERE t.id = :team_id
            """),
            {
                "team_id": team_id,
                "user_id": current_user.id
            }
        )
        team = team.fetchone()
        
        logger.info(f"Team data: {team}")
        logger.info(f"Current user ID: {current_user.id}")
        logger.info(f"Team captain ID: {team.captain_id}")
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Проверяем, является ли пользователь капитаном команды
        if team.captain_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Only team captain can register team for tournament"
            )

        # Проверяем, не участвует ли команда уже в турнире
        existing = await db.execute(
            text("""
                SELECT 1 FROM tournament_teams 
                WHERE tournament_id = :tournament_id AND team_id = :team_id
            """),
            {"tournament_id": tournament_id, "team_id": team_id}
        )
        if existing.fetchone():
            raise HTTPException(
                status_code=400, 
                detail="Team is already registered for this tournament"
            )

        # Добавляем команду в турнир
        await db.execute(
            text("""
                INSERT INTO tournament_teams (tournament_id, team_id)
                VALUES (:tournament_id, :team_id)
            """),
            {"tournament_id": tournament_id, "team_id": team_id}
        )
        await db.commit()

        return {"status": "success", "message": "Team successfully registered for tournament"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error joining tournament: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/{tournament_id}/leave")
async def leave_tournament(
    tournament_id: int,
    team_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        team_id = team_data.get("team_id")
        if not team_id:
            raise HTTPException(status_code=400, detail="Team ID is required")

        # Проверяем существование турнира
        tournament = await db.execute(
            text("""
                SELECT t.*, tt.team_id 
                FROM tournaments t
                LEFT JOIN tournament_teams tt ON tt.tournament_id = t.id
                WHERE t.id = :id
            """),
            {"id": tournament_id}
        )
        tournament = tournament.fetchone()
        if not tournament:
            raise HTTPException(status_code=404, detail="Tournament not found")

        # Проверяем существование команды и права пользователя
        team = await db.execute(
            text("""
                SELECT t.*, 
                       CASE 
                           WHEN t.captain_id = :user_id THEN true
                           WHEN EXISTS (
                               SELECT 1 FROM team_members 
                               WHERE team_id = t.id AND user_id = :user_id
                           ) THEN true
                           ELSE false
                       END as is_member
                FROM teams t
                WHERE t.id = :team_id
            """),
            {
                "team_id": team_id,
                "user_id": current_user.id
            }
        )
        team = team.fetchone()
        
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Разрешаем выход из турнира как капитану, так и участникам команды
        if not team.is_member:
            raise HTTPException(
                status_code=403,
                detail="Only team members can remove team from tournament"
            )

        # Проверяем, участвует ли команда в турнире
        existing = await db.execute(
            text("""
                SELECT 1 FROM tournament_teams 
                WHERE tournament_id = :tournament_id AND team_id = :team_id
            """),
            {"tournament_id": tournament_id, "team_id": team_id}
        )
        if not existing.fetchone():
            raise HTTPException(
                status_code=404,
                detail="Team is not registered for this tournament"
            )

        # Удаляем команду из турнира
        await db.execute(
            text("""
                DELETE FROM tournament_teams 
                WHERE tournament_id = :tournament_id AND team_id = :team_id
            """),
            {"tournament_id": tournament_id, "team_id": team_id}
        )
        await db.commit()

        return {"status": "success", "message": "Team successfully left the tournament"}

    except HTTPException:
        await db.rollback()
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Error leaving tournament: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
