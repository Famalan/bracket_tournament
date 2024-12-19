"""add captain_id to teams

Revision ID: f57b4a4d8ad0
Revises: 6af44b29fafc
Create Date: 2024-12-14 03:14:31.900914+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f57b4a4d8ad0'
down_revision: Union[str, None] = '6af44b29fafc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Добавляем foreign key
    op.create_foreign_key(
        'fk_team_captain',
        'teams', 'users',
        ['captain_id'], ['id'],
        ondelete='SET NULL'
    )

def downgrade() -> None:
    # Удаляем foreign key
    op.drop_constraint('fk_team_captain', 'teams', type_='foreignkey')