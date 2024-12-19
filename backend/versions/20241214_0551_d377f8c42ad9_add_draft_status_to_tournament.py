"""add draft status to tournament

Revision ID: d377f8c42ad9
Revises: c8d0f3773c4a
Create Date: 2024-12-14 05:51:10.797861+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd377f8c42ad9'
down_revision: Union[str, None] = 'c8d0f3773c4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass 