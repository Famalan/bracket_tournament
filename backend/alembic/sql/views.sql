-- Здесь будут храниться определения представлений

-- Пример представления для активных турниров
CREATE OR REPLACE VIEW active_tournaments AS
SELECT *
FROM tournaments
WHERE status = 'active'; 