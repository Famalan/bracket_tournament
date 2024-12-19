-- Добавление администратора и тестовых пользователей
INSERT INTO users (username, email, hashed_password, role) VALUES
    ('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCJzjkQzy', 'admin'),  -- пароль: admin
    ('organizer1', 'org1@example.com', '$2b$12$dNmNDKSeZOhp.NbujwOXn.LxL27mKGYP.jcJ8Gq0RJIKGvVH8P3z2', 'organizer'),  -- пароль: organizer
    ('organizer2', 'org2@example.com', '$2b$12$dNmNDKSeZOhp.NbujwOXn.LxL27mKGYP.jcJ8Gq0RJIKGvVH8P3z2', 'organizer'),  -- пароль: organizer
    ('player1', 'player1@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCJzjkQzy', 'player'),  -- пароль: player
    ('player2', 'player2@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCJzjkQzy', 'player'),  -- пароль: player
    ('player3', 'player3@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCJzjkQzy', 'player'),  -- пароль: player
    ('player4', 'player4@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCJzjkQzy', 'player');  -- пароль: player

-- Создание тестовых турниров
INSERT INTO tournaments (name, description, type, status, rules, max_teams, registration_deadline, start_date, end_date, created_by) VALUES
    ('CS:GO Summer Cup 2024', 'Летний турнир по CS:GO', 'single_elimination', 'registration', 'Стандартные правила CS:GO', 8, 
     CURRENT_TIMESTAMP + INTERVAL '7 days', CURRENT_TIMESTAMP + INTERVAL '14 days', CURRENT_TIMESTAMP + INTERVAL '16 days', 2),
    ('Dota 2 Championship', 'Чемпионат по Dota 2', 'double_elimination', 'registration', 'Стандартные правила Dota 2', 16,
     CURRENT_TIMESTAMP + INTERVAL '14 days', CURRENT_TIMESTAMP + INTERVAL '21 days', CURRENT_TIMESTAMP + INTERVAL '25 days', 2),
    ('League Round Robin', 'Круговой турнир по League of Legends', 'round_robin', 'draft', 'Правила LoL', 4,
     CURRENT_TIMESTAMP + INTERVAL '30 days', CURRENT_TIMESTAMP + INTERVAL '45 days', CURRENT_TIMESTAMP + INTERVAL '50 days', 3);

-- Создание тестовых команд
INSERT INTO teams (name, description, captain_id) VALUES
    ('Phoenix Force', 'Опытная команда по CS:GO', 4),
    ('Dragon Warriors', 'Профессиональная команда Dota 2', 5),
    ('Cyber Knights', 'Команда энтузиастов', 6),
    ('Digital Legends', 'Мо��одая перспективная команда', 7);

-- Добавление игроков в команды
INSERT INTO players (user_id, team_id, nickname) VALUES
    (4, 1, 'Phoenix1'),
    (5, 2, 'Dragon1'),
    (6, 3, 'Knight1'),
    (7, 4, 'Legend1');

-- Регистрация команд на турниры
INSERT INTO tournament_teams (tournament_id, team_id, status) VALUES
    (1, 1, 'accepted'),
    (1, 2, 'accepted'),
    (1, 3, 'pending'),
    (2, 2, 'accepted'),
    (2, 3, 'accepted'),
    (2, 4, 'pending');

-- Создание тестовых матчей
INSERT INTO matches (tournament_id, team1_id, team2_id, start_time, status) VALUES
    (1, 1, 2, CURRENT_TIMESTAMP + INTERVAL '15 days', 'scheduled'),
    (2, 2, 3, CURRENT_TIMESTAMP + INTERVAL '22 days', 'scheduled');

-- Создание структуры турнирной сетки
INSERT INTO bracket (tournament_id, match_id, round, position) VALUES
    (1, 1, 1, 1),
    (2, 2, 1, 1);

-- Добавление тестовой резервной копии
INSERT INTO backup (file_path, description, file_size, created_by) VALUES
    ('/backups/tournament_db_backup_2024_03_15.sql', 'Еженедельное резервное копирование', 1048576, 1); 