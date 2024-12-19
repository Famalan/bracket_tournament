"""update user roles to uppercase

Revision ID: 9b2a51c49b8b
Revises: None
Create Date: 2024-12-13 22:16:14.003534+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9b2a51c49b8b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

dbranch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Удаляем дефолтное значение
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    
    # Временно изменяем тип колонки на string
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50) USING role::VARCHAR")
    
    # Обновляем значения
    op.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'admin'")
    op.execute("UPDATE users SET role = 'ORGANIZER' WHERE role = 'organizer'")
    op.execute("UPDATE users SET role = 'PLAYER' WHERE role = 'player'")
    
    # Удаляем старый enum тип
    op.execute("DROP TYPE user_role")
    
    # Создаем новый enum тип
    op.execute("CREATE TYPE user_role AS ENUM ('ADMIN', 'ORGANIZER', 'PLAYER')")
    
    # Меняем тип колонки обратно на enum и устанавливаем дефолтное значение
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'PLAYER'::user_role")

def downgrade() -> None:
    # Удаляем дефолтное значение
    op.execute("ALTER TABLE users ALTER COLUMN role DROP DEFAULT")
    
    # Временно изменяем тип колонки на string
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(50) USING role::VARCHAR")
    
    # Обновляем значения обратно
    op.execute("UPDATE users SET role = 'admin' WHERE role = 'ADMIN'")
    op.execute("UPDATE users SET role = 'organizer' WHERE role = 'ORGANIZER'")
    op.execute("UPDATE users SET role = 'player' WHERE role = 'PLAYER'")
    
    # Удаляем новый enum тип
    op.execute("DROP TYPE user_role")
    
    # Создаем старый enum тип
    op.execute("CREATE TYPE user_role AS ENUM ('admin', 'organizer', 'player')")
    
    # Меняем тип колонки обратно на enum и устанавливаем дефолтное значение
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE user_role USING role::user_role")
    op.execute("ALTER TABLE users ALTER COLUMN role SET DEFAULT 'player'::user_role")