from fastapi import APIRouter
from app.api.v1 import auth, users, tournaments, teams

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(tournaments.router, prefix="/tournaments", tags=["tournaments"])
api_router.include_router(teams.router, prefix="/teams", tags=["teams"])

__all__ = ["users", "tournaments", "auth", "teams"] 