from sqlalchemy import Column, Integer, DateTime, ForeignKey, Table
from app.db.base_class import Base
from sqlalchemy.sql import func

tournament_teams = Table(
    'tournament_teams',
    Base.metadata,
    Column('tournament_id', Integer, ForeignKey('tournaments.id', ondelete='CASCADE'), primary_key=True),
    Column('team_id', Integer, ForeignKey('teams.id', ondelete='CASCADE'), primary_key=True),
    Column('joined_at', DateTime, server_default=func.now())
) 