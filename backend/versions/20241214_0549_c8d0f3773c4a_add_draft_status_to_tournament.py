"""add draft status to tournament

Revision ID: c8d0f3773c4a
Revises: f57b4a4d8ad0
Create Date: 2024-12-14 05:49:09.036214+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c8d0f3773c4a'
down_revision: Union[str, None] = 'f57b4a4d8ad0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Создаем временную таблицу
    op.execute("ALTER TABLE tournaments ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    op.execute("DROP TYPE tournamentstatus")
    op.execute("CREATE TYPE tournamentstatus AS ENUM ('draft', 'registration', 'in_progress', 'completed')")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE tournamentstatus USING status::tournamentstatus")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status SET DEFAULT 'draft'")

def downgrade():
    # Откатываем изменения
    op.execute("ALTER TABLE tournaments ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    op.execute("DROP TYPE tournamentstatus")
    op.execute("CREATE TYPE tournamentstatus AS ENUM ('registration', 'in_progress', 'completed')")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE tournamentstatus USING status::tournamentstatus")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status SET DEFAULT 'registration'")