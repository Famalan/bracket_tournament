from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy import text
from app.models import Base
from app.models.user import User, UserRole
from app.models.team import Team
from app.models.team_member import TeamMember

async def create_tables(engine: AsyncEngine):
    async with engine.begin() as conn:
        # Создаем тип enum для ролей пользователей
        await conn.execute(text("""
            DO $$ 
            BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'user_role') THEN
                    CREATE TYPE user_role AS ENUM ('ADMIN', 'ORGANIZER', 'PLAYER');
                END IF;
            END
            $$;
        """))
        
        # Создаем таблицы
        await conn.run_sync(Base.metadata.create_all) 