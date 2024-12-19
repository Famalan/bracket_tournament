#!/bin/bash

# Активируем виртуальное окружение
source venv/bin/activate

# Применяем схему базы данных
python scripts/apply_schema.py

# Инициализируем начальные данные
python scripts/init_db.py