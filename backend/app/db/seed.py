from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.security import get_password_hash
from app.models.user import UserRole

async def seed_db(db: AsyncSession) -> None:
    try:
        # 1. Создание тестовых пользователей
        test_users = [
            ("admin", "admin@example.com", "admin", "admin"),
            ("organizer1", "org1@example.com", "organizer", "organizer"),
            ("organizer2", "org2@example.com", "organizer", "organizer"),
            ("player1", "player1@example.com", "player", "player"),
            ("player2", "player2@example.com", "player", "player"),
            ("player3", "player3@example.com", "player", "player"),
            ("player4", "player4@example.com", "player", "player"),
        ]
        
        for username, email, password, role in test_users:
            query = text("""
                INSERT INTO users (username, email, hashed_password, role)
                VALUES (:username, :email, :hashed_password, :role)
                ON CONFLICT (username) DO NOTHING
                RETURNING id;
            """)
            
            await db.execute(
                query,
                {
                    "username": username,
                    "email": email,
                    "hashed_password": get_password_hash(password),
                    "role": role
                }
            )
            
        # 2. Создание тестовых турниров
        tournaments_data = [
            ("CS:GO Summer Cup 2024", "Летний турнир по CS:GO", "single_elimination", 
             "registration", "Стандартные правила CS:GO", 8, 2),
            ("Dota 2 Championship", "Чемпионат по Dota 2", "double_elimination", 
             "registration", "Стандартные правила Dota 2", 16, 2),
            ("League Round Robin", "Круговой турнир по League of Legends", "round_robin", 
             "draft", "Правила LoL", 4, 3),
        ]
        
        for name, desc, type_, status, rules, max_teams, created_by in tournaments_data:
            query = text("""
                INSERT INTO tournaments (name, description, type, status, rules, max_teams, 
                                      registration_deadline, start_date, end_date, created_by)
                VALUES (:name, :description, :type, :status, :rules, :max_teams,
                        CURRENT_TIMESTAMP + INTERVAL '7 days',
                        CURRENT_TIMESTAMP + INTERVAL '14 days',
                        CURRENT_TIMESTAMP + INTERVAL '16 days',
                        :created_by)
                ON CONFLICT (name) DO NOTHING
                RETURNING id;
            """)
            
            await db.execute(
                query,
                {
                    "name": name,
                    "description": desc,
                    "type": type_,
                    "status": status,
                    "rules": rules,
                    "max_teams": max_teams,
                    "created_by": created_by
                }
            )
            
        # 3. Создание тестовых команд
        teams_data = [
            ("Phoenix Force", "Опытная команда по CS:GO", 4),
            ("Dragon Warriors", "Профессиональная команда Dota 2", 5),
            ("Cyber Knights", "Команда энтузиастов", 6),
            ("Digital Legends", "Молодая перспективная команда", 7),
        ]
        
        for name, desc, captain_id in teams_data:
            query = text("""
                INSERT INTO teams (name, description, captain_id)
                VALUES (:name, :description, :captain_id)
                ON CONFLICT (name) DO NOTHING
                RETURNING id;
            """)
            
            await db.execute(
                query,
                {
                    "name": name,
                    "description": desc,
                    "captain_id": captain_id
                }
            )

        # 4. Добавление игроков в команды
        players_data = [
            (4, 1, "Phoenix1"),
            (5, 2, "Dragon1"),
            (6, 3, "Knight1"),
            (7, 4, "Legend1"),
        ]

        for user_id, team_id, nickname in players_data:
            query = text("""
                INSERT INTO players (user_id, team_id, nickname)
                VALUES (:user_id, :team_id, :nickname)
                ON CONFLICT (user_id, team_id) DO NOTHING;
            """)
            
            await db.execute(query, {
                "user_id": user_id,
                "team_id": team_id,
                "nickname": nickname
            })

        await db.commit()
        print("Тестовые данные успешно добавлены")
        
    except Exception as e:
        await db.rollback()
        print(f"Ошибка при добавлении тестовых данных: {e}")
        raise