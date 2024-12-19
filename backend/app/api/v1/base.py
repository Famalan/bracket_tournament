from fastapi import APIRouter
from app.api.v1 import (
    auth,
    users,
    tournaments,
    teams,
    matches,
    brackets,
    backup
)

api_router = APIRouter()

# Группировка роутеров по функциональности
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tournaments.router, prefix="/tournaments", tags=["tournaments"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])
api_router.include_router(matches.router, prefix="/matches", tags=["matches"])
api_router.include_router(brackets.router, prefix="/brackets", tags=["brackets"])
api_router.include_router(backup.router, prefix="/backup", tags=["backup"]) 