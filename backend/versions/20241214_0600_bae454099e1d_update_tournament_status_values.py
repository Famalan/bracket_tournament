"""update tournament status values

Revision ID: bae454099e1d
Revises: d377f8c42ad9
Create Date: 2024-12-14 06:00:46.563863+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'bae454099e1d'
down_revision: Union[str, None] = 'd377f8c42ad9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Сначала изменим тип на VARCHAR
    op.execute("ALTER TABLE tournaments ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    op.execute("DROP TYPE tournamentstatus")

    # Обновим значения
    op.execute("UPDATE tournaments SET status = 'DRAFT' WHERE status = 'draft'")
    op.execute("UPDATE tournaments SET status = 'REGISTRATION' WHERE status = 'registration'")
    op.execute("UPDATE tournaments SET status = 'IN_PROGRESS' WHERE status = 'in_progress'")
    op.execute("UPDATE tournaments SET status = 'COMPLETED' WHERE status = 'completed'")

    # Создадим новый enum и изменим тип колонки
    op.execute("CREATE TYPE tournamentstatus AS ENUM ('DRAFT', 'REGISTRATION', 'IN_PROGRESS', 'COMPLETED')")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE tournamentstatus USING status::tournamentstatus")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status SET DEFAULT 'DRAFT'")

def downgrade():
    # Сначала изменим тип на VARCHAR
    op.execute("ALTER TABLE tournaments ALTER COLUMN status DROP DEFAULT")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE VARCHAR USING status::VARCHAR")
    op.execute("DROP TYPE tournamentstatus")

    # Обновим значения
    op.execute("UPDATE tournaments SET status = 'draft' WHERE status = 'DRAFT'")
    op.execute("UPDATE tournaments SET status = 'registration' WHERE status = 'REGISTRATION'")
    op.execute("UPDATE tournaments SET status = 'in_progress' WHERE status = 'IN_PROGRESS'")
    op.execute("UPDATE tournaments SET status = 'completed' WHERE status = 'COMPLETED'")

    # Создадим старый enum и изменим тип колонки
    op.execute("CREATE TYPE tournamentstatus AS ENUM ('draft', 'registration', 'in_progress', 'completed')")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status TYPE tournamentstatus USING status::tournamentstatus")
    op.execute("ALTER TABLE tournaments ALTER COLUMN status SET DEFAULT 'draft'")