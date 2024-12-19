"""create tournament teams table

Revision ID: create_tournament_teams
Revises: previous_revision
Create Date: 2024-12-18 17:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'create_tournament_teams'
down_revision = 'previous_revision'  # Укажите ID предыдущей миграции
branch_labels = None
depends_on = None

def upgrade() -> None:
    op.create_table(
        'tournament_teams',
        sa.Column('tournament_id', sa.Integer(), nullable=False),
        sa.Column('team_id', sa.Integer(), nullable=False),
        sa.Column('joined_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('tournament_id', 'team_id')
    )
    
    # Создаем индексы для оптимизации запросов
    op.create_index(
        'ix_tournament_teams_tournament_id',
        'tournament_teams',
        ['tournament_id']
    )
    op.create_index(
        'ix_tournament_teams_team_id',
        'tournament_teams',
        ['team_id']
    )

def downgrade() -> None:
    op.drop_index('ix_tournament_teams_team_id')
    op.drop_index('ix_tournament_teams_tournament_id')
    op.drop_table('tournament_teams') 