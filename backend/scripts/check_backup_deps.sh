#!/bin/bash

# Проверка наличия pg_dump и pg_restore
check_pg_tools() {
    if ! command -v pg_dump &> /dev/null; then
        echo "pg_dump не найден. Установка PostgreSQL утилит..."
        sudo apt-get update && sudo apt-get install -y postgresql-client
    fi
    
    if ! command -v pg_restore &> /dev/null; then
        echo "pg_restore не найден. Установка PostgreSQL утилит..."
        sudo apt-get update && sudo apt-get install -y postgresql-client
    fi
}

# Создание директории для бэкапов и настройка прав
setup_backup_dir() {
    BACKUP_DIR="backups"
    if [ ! -d "$BACKUP_DIR" ]; then
        mkdir -p "$BACKUP_DIR"
        echo "Создана директория для бэкапов: $BACKUP_DIR"
    fi
    
    # Настройка прав доступа
    chmod 750 "$BACKUP_DIR"
    echo "Настроены права доступа для директории бэкапов"
}

# Запуск проверок
check_pg_tools
setup_backup_dir 