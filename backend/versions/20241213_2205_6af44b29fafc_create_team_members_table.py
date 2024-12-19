"""create team members table

Revision ID: 6af44b29fafc
Revises: 9b2a51c49b8b
Create Date: 2024-12-13 22:05:25.000893+00:00

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = '6af44b29fafc'
down_revision: Union[str, None] = '9b2a51c49b8b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Проверяем существование таблицы
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'team_members' not in tables:
        op.create_table(
            'team_members',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('team_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_team_members_id'), 'team_members', ['id'], unique=False)

def downgrade() -> None:
    op.drop_index(op.f('ix_team_members_id'), table_name='team_members')
    op.drop_table('team_members')

