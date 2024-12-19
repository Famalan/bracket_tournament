from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .models import Tournament, Team, User
from .database import get_db
from .auth import get_current_user

router = APIRouter()

@router.post("/{tournament_id}/join")
async def join_tournament(
    tournament_id: int,
    team_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_id = team_data.get("team_id")
    if not team_id:
        raise HTTPException(status_code=400, detail="Team ID is required")

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Проверяем, является ли пользователь капитаном команды
    if team.captain_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only team captain can register team for tournament",
        )

    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status != "registration":
        raise HTTPException(
            status_code=400, detail="Tournament is not in registration phase"
        )

    # Проверяем, не участвует ли команда уже в турнире
    if team in tournament.teams:
        raise HTTPException(
            status_code=400, detail="Team is already registered for this tournament"
        )

    tournament.teams.append(team)
    db.commit()

    return {"status": "success"}

@router.post("/{tournament_id}/leave")
async def leave_tournament(
    tournament_id: int,
    team_data: dict = Body(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    team_id = team_data.get("team_id")
    if not team_id:
        raise HTTPException(status_code=400, detail="Team ID is required")

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    if team.captain_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Only team captain can remove team from tournament",
        )

    tournament = db.query(Tournament).filter(Tournament.id == tournament_id).first()
    if not tournament:
        raise HTTPException(status_code=404, detail="Tournament not found")

    if tournament.status != "registration":
        raise HTTPException(
            status_code=400,
            detail="Cannot leave tournament after registration phase",
        )

    if team not in tournament.teams:
        raise HTTPException(
            status_code=400, detail="Team is not registered for this tournament"
        )

    tournament.teams.remove(team)
    db.commit()

    return {"status": "success"} 