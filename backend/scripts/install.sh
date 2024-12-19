#!/bin/bash

# Создаем виртуальное окружение
python3.11 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt

# Делаем скрипты исполняемыми
chmod +x scripts/*.sh

# Проверяем зависимости для бэкапов
./scripts/check_backup_deps.sh

# Настраиваем базу данных
./scripts/setup_db.sh

echo "Установка завершена" 