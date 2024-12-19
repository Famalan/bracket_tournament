from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import UserRole
from app.core.security import get_password_hash
from sqlalchemy import text
from app.db.check_db import check_tables

async def init_db(db: AsyncSession) -> None:
    try:
        # Проверяем существование таблиц
        tables_info = await check_tables(db)
        if not tables_info.get("tables_exist"):
            print(f"Отсутствуют необходимые таблицы. Существующие таблицы: {tables_info.get('existing_tables')}")
            return

        # Проверяем наличие пользователей
        check_users_query = text("SELECT COUNT(*) FROM users")
        result = await db.execute(check_users_query)
        users_count = result.scalar()

        if users_count == 0:
            print("Создание тестовых пользователей...")
            # Создаем базовых пользователей
            base_users_query = text("""
                INSERT INTO users (username, email, hashed_password, role, is_active)
                VALUES 
                ('admin', 'admin@example.com', :admin_pass, 'ADMIN', true),
                ('player1', 'player1@example.com', :player_pass, 'PLAYER', true),
                ('player2', 'player2@example.com', :player_pass, 'PLAYER', true),
                ('player3', 'player3@example.com', :player_pass, 'PLAYER', true)
                ON CONFLICT (username) DO NOTHING
                RETURNING id
            """)
            
            await db.execute(base_users_query, {
                "admin_pass": get_password_hash("admin"),
                "player_pass": get_password_hash("player123")
            })
            await db.commit()
            print("Тестовые пользователи созданы")

        # Проверяем наличие команд
        check_teams_query = text("SELECT COUNT(*) FROM teams")
        result = await db.execute(check_teams_query)
        teams_count = result.scalar()

        if teams_count == 0:
            print("Создание тестовых команд...")
            teams_query = text("""
                INSERT INTO teams (name, captain_id)
                SELECT 
                    t.name, 
                    u.id as captain_id
                FROM (
                    VALUES 
                    ('Team Alpha', 'player1'),
                    ('Digital Dragons', 'player2'),
                    ('Cyber Knights', 'player3')
                ) as t(name, captain_username)
                JOIN users u ON u.username = t.captain_username
                RETURNING id
            """)
            
            teams_result = await db.execute(teams_query)
            team_ids = teams_result.fetchall()
            await db.commit()
            print("Тестовые команды созданы")

    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
        await db.rollback()
        raise