import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import asyncio
import asyncpg
from app.core.config import settings

async def apply_schema():
    # Подключаемся к базе данных
    conn = await asyncpg.connect(
        user=settings.POSTGRES_USER,
        password=settings.POSTGRES_PASSWORD,
        database=settings.POSTGRES_DB,
        host=settings.POSTGRES_SERVER,
        port=settings.POSTGRES_PORT
    )

    try:
        # Удаляем существующие типы
        types_to_drop = ['user_role', 'tournament_type', 'tournament_status']
        for type_name in types_to_drop:
            try:
                await conn.execute(f'DROP TYPE IF EXISTS {type_name} CASCADE;')
                print(f"Dropped type {type_name}")
            except Exception as e:
                print(f"Warning while dropping type {type_name}: {e}")

        # Удаляем существующие таблицы
        tables_to_drop = [
            'tournaments',
            'teams',
            'tournament_teams',
            'users',
            'matches',
            'tournament_participants',
            'team_members',
            'alembic_version',  # если используете alembic для миграций
            'players',  # добавили новую таблицу
            'bracket',  # добавленная таблица
            'backup'  # Добавили таблицу backup
        ]
        
        for table_name in tables_to_drop:
            try:
                await conn.execute(f'DROP TABLE IF EXISTS {table_name} CASCADE;')
                print(f"Dropped table {table_name}")
            except Exception as e:
                print(f"Warning while dropping table {table_name}: {e}")

        # Читаем SQL-файл
        with open('alembic/sql/init.sql', 'r') as f:
            sql = f.read()

        # Выполняем SQL-скрипт
        await conn.execute(sql)
        print("Schema applied successfully")

    except Exception as e:
        print(f"Error applying schema: {e}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(apply_schema()) 