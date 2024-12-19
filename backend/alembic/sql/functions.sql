-- Здесь будут храниться определения функций

-- Пример функции для обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql'; 

-- Представление для просмотра статистики турниров
CREATE OR REPLACE VIEW tournament_statistics AS
SELECT 
    t.id AS tournament_id,
    t.name AS tournament_name,
    t.status,
    COUNT(DISTINCT tt.team_id) AS registered_teams,
    t.max_teams,
    COUNT(DISTINCT m.id) AS matches_count,
    COUNT(DISTINCT CASE WHEN m.status = 'completed' THEN m.id END) AS completed_matches
FROM tournaments t
LEFT JOIN tournament_teams tt ON t.id = tt.tournament_id
LEFT JOIN matches m ON t.id = m.tournament_id
GROUP BY t.id, t.name, t.status, t.max_teams;

-- Представление для просмотра результатов команд
CREATE OR REPLACE VIEW team_results AS
SELECT 
    t.id AS team_id,
    t.name AS team_name,
    COUNT(DISTINCT m.id) AS total_matches,
    COUNT(DISTINCT CASE WHEN m.winner_id = t.id THEN m.id END) AS wins,
    COUNT(DISTINCT CASE WHEN m.status = 'completed' AND m.winner_id != t.id THEN m.id END) AS losses
FROM teams t
LEFT JOIN matches m ON (t.id = m.team1_id OR t.id = m.team2_id) AND m.status = 'completed'
GROUP BY t.id, t.name;

-- Функция для проверки возможности регистрации команды на турнир
CREATE OR REPLACE FUNCTION check_tournament_registration(
    p_tournament_id INTEGER,
    p_team_id INTEGER
) RETURNS BOOLEAN AS $$
DECLARE
    current_teams INTEGER;
    max_teams INTEGER;
    tournament_status tournament_status;
BEGIN
    -- Получаем текущее количество команд и максимально допустимое
    SELECT 
        COUNT(*), 
        t.max_teams,
        t.status
    INTO current_teams, max_teams, tournament_status
    FROM tournaments t
    LEFT JOIN tournament_teams tt ON t.id = tt.tournament_id
    WHERE t.id = p_tournament_id
    GROUP BY t.max_teams, t.status;

    -- Проверяем условия
    RETURN 
        tournament_status = 'registration' AND
        current_teams < max_teams;
END;
$$ LANGUAGE plpgsql;

-- Триггеры для обновления updated_at
CREATE TRIGGER update_users_modtime
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tournaments_modtime
    BEFORE UPDATE ON tournaments
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_teams_modtime
    BEFORE UPDATE ON teams
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Триггер для проверки регистрации команды на турнир
CREATE OR REPLACE FUNCTION check_team_registration()
RETURNS TRIGGER AS $$
BEGIN
    IF NOT check_tournament_registration(NEW.tournament_id, NEW.team_id) THEN
        RAISE EXCEPTION 'Регистрация на турнир невозможна';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_team_registration_trigger
    BEFORE INSERT ON tournament_teams
    FOR EACH ROW
    EXECUTE FUNCTION check_team_registration();

-- Функции для работы с турнирами
CREATE OR REPLACE FUNCTION get_tournament_standings(p_tournament_id INTEGER)
RETURNS TABLE (
    team_id INTEGER,
    team_name VARCHAR,
    matches_played INTEGER,
    wins INTEGER,
    losses INTEGER,
    points INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.id AS team_id,
        t.name AS team_name,
        COUNT(DISTINCT m.id) AS matches_played,
        COUNT(DISTINCT CASE WHEN m.winner_id = t.id THEN m.id END) AS wins,
        COUNT(DISTINCT CASE WHEN m.status = 'completed' AND m.winner_id != t.id THEN m.id END) AS losses,
        COUNT(DISTINCT CASE WHEN m.winner_id = t.id THEN m.id END) * 3 AS points
    FROM teams t
    JOIN tournament_teams tt ON t.id = tt.team_id
    LEFT JOIN matches m ON (t.id = m.team1_id OR t.id = m.team2_id) 
        AND m.tournament_id = p_tournament_id
    WHERE tt.tournament_id = p_tournament_id
    GROUP BY t.id, t.name
    ORDER BY points DESC;
END;
$$ LANGUAGE plpgsql;

-- Процедура для автоматического создания матчей в турнире
CREATE OR REPLACE PROCEDURE generate_tournament_matches(
    p_tournament_id INTEGER
) AS $$
DECLARE
    v_team_count INTEGER;
    v_team_ids INTEGER[];
    v_tournament_type tournament_type;
    v_round INTEGER := 1;
    v_position INTEGER := 1;
    v_match_id INTEGER;
BEGIN
    -- Получаем тип турнира и список команд
    SELECT 
        t.type,
        ARRAY_AGG(tt.team_id ORDER BY RANDOM())
    INTO v_tournament_type, v_team_ids
    FROM tournaments t
    JOIN tournament_teams tt ON t.id = tt.tournament_id
    WHERE t.id = p_tournament_id AND tt.status = 'accepted'
    GROUP BY t.type;

    v_team_count := ARRAY_LENGTH(v_team_ids, 1);

    -- Создаем матчи в зависимости от типа турнира
    IF v_tournament_type = 'single_elimination' THEN
        FOR i IN 1..v_team_count/2 LOOP
            -- Создаем матч
            INSERT INTO matches (
                tournament_id, 
                team1_id, 
                team2_id, 
                start_time,
                status
            ) VALUES (
                p_tournament_id,
                v_team_ids[i*2-1],
                v_team_ids[i*2],
                CURRENT_TIMESTAMP + (i || ' hours')::INTERVAL,
                'scheduled'
            ) RETURNING id INTO v_match_id;

            -- Добавляем в сетку
            INSERT INTO bracket (
                tournament_id,
                match_id,
                round,
                position
            ) VALUES (
                p_tournament_id,
                v_match_id,
                v_round,
                v_position
            );
            
            v_position := v_position + 1;
        END LOOP;
    END IF;

    -- Обновляем статус турнира
    UPDATE tournaments 
    SET status = 'in_progress'
    WHERE id = p_tournament_id;
END;
$$ LANGUAGE plpgsql;

-- Функция для обновления статистики матча
CREATE OR REPLACE FUNCTION update_match_statistics()
RETURNS TRIGGER AS $$
BEGIN
    -- Если матч завершен, определяем победителя
    IF NEW.status = 'completed' AND OLD.status != 'completed' THEN
        IF NEW.score_team1 > NEW.score_team2 THEN
            NEW.winner_id := NEW.team1_id;
        ELSIF NEW.score_team2 > NEW.score_team1 THEN
            NEW.winner_id := NEW.team2_id;
        END IF;
        
        -- Устанавливаем время окончания
        NEW.end_time := CURRENT_TIMESTAMP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Представления
CREATE OR REPLACE VIEW active_tournaments AS
SELECT 
    t.*,
    COUNT(DISTINCT tt.team_id) AS current_teams
FROM tournaments t
LEFT JOIN tournament_teams tt ON t.id = tt.tournament_id
WHERE t.status IN ('registration', 'in_progress')
GROUP BY t.id;

-- Функция для получения следующего матча команды
CREATE OR REPLACE FUNCTION get_next_team_match(p_team_id INTEGER)
RETURNS TABLE (
    match_id INTEGER,
    tournament_name VARCHAR,
    opponent_name VARCHAR,
    start_time TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.id AS match_id,
        t.name AS tournament_name,
        CASE 
            WHEN m.team1_id = p_team_id THEN t2.name
            ELSE t1.name
        END AS opponent_name,
        m.start_time
    FROM matches m
    JOIN tournaments t ON m.tournament_id = t.id
    JOIN teams t1 ON m.team1_id = t1.id
    JOIN teams t2 ON m.team2_id = t2.id
    WHERE (m.team1_id = p_team_id OR m.team2_id = p_team_id)
        AND m.status = 'scheduled'
        AND m.start_time > CURRENT_TIMESTAMP
    ORDER BY m.start_time
    LIMIT 1;
END;
$$ LANGUAGE plpgsql;