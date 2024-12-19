#!/bin/bash

# Активируем виртуальное окружение
source venv/bin/activate

# Запускаем сервер
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 