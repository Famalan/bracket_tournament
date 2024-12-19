from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from fastapi import HTTPException
from typing import List, Optional
import subprocess
import os
from datetime import datetime

from app.core.config import settings

class BackupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.backup_dir = "backups"
        
        # Создаем директорию для бэкапов, если её нет
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)

    async def create_backup(self, user_id: int) -> dict:
        """Создание резервной копии базы данных"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"backup_{timestamp}.sql"
        filepath = os.path.join(self.backup_dir, filename)

        try:
            # Создаем дамп базы данных через pg_dump
            command = [
                'pg_dump',
                f'--dbname=postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}',
                '--format=custom',
                f'--file={filepath}'
            ]
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                raise Exception(f"Ошибка при создании бэкапа: {process.stderr}")

            # Получаем размер файла
            file_size = os.path.getsize(filepath)

            # Записываем информацию о бэкапе в базу данных
            query = text("""
                INSERT INTO backup (
                    file_path,
                    description,
                    file_size,
                    created_by
                )
                VALUES (
                    :file_path,
                    :description,
                    :file_size,
                    :created_by
                )
                RETURNING *
            """)
            
            result = await self.db.execute(
                query,
                {
                    "file_path": filepath,
                    "description": f"Автоматический бэкап от {timestamp}",
                    "file_size": file_size,
                    "created_by": user_id
                }
            )
            await self.db.commit()
            
            return result.fetchone()

        except Exception as e:
            await self.db.rollback()
            if os.path.exists(filepath):
                os.remove(filepath)
            raise HTTPException(status_code=500, detail=f"Ошибка создания бэкапа: {str(e)}")

    async def restore_backup(self, backup_id: int, user_id: int) -> dict:
        """Восстановление базы данных из резервной копии"""
        # Получаем информацию о бэкапе
        query = text("SELECT * FROM backup WHERE id = :backup_id")
        result = await self.db.execute(query, {"backup_id": backup_id})
        backup = result.fetchone()

        if not backup:
            raise HTTPException(status_code=404, detail="Бэкап не найден")

        try:
            # Восстанавливаем базу данных через pg_restore
            command = [
                'pg_restore',
                '--clean',  # Очищаем существующие данные
                '--if-exists',
                f'--dbname=postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_SERVER}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}',
                backup.file_path
            ]
            
            process = subprocess.run(
                command,
                capture_output=True,
                text=True
            )
            
            if process.returncode != 0:
                raise Exception(f"Ошибка при восстановлении: {process.stderr}")

            # Обновляем информацию о восстановлении
            query = text("""
                UPDATE backup
                SET restored_at = CURRENT_TIMESTAMP,
                    restored_by = :user_id
                WHERE id = :backup_id
                RETURNING *
            """)
            
            result = await self.db.execute(
                query,
                {
                    "backup_id": backup_id,
                    "user_id": user_id
                }
            )
            await self.db.commit()
            
            return result.fetchone()

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка восстановления из бэкапа: {str(e)}"
            )

    async def get_backups(self, skip: int = 0, limit: int = 10) -> List[dict]:
        """Получение списка резервных копий"""
        query = text("""
            SELECT 
                b.*,
                c.username as created_by_username,
                r.username as restored_by_username
            FROM backup b
            LEFT JOIN users c ON b.created_by = c.id
            LEFT JOIN users r ON b.restored_by = r.id
            ORDER BY b.created_at DESC
            LIMIT :limit OFFSET :skip
        """)
        
        result = await self.db.execute(query, {"limit": limit, "skip": skip})
        return result.fetchall()

    async def delete_backup(self, backup_id: int) -> None:
        """Удаление резервной копии"""
        query = text("SELECT file_path FROM backup WHERE id = :backup_id")
        result = await self.db.execute(query, {"backup_id": backup_id})
        backup = result.fetchone()

        if not backup:
            raise HTTPException(status_code=404, detail="Бэкап не найден")

        try:
            # Удаляем файл
            if os.path.exists(backup.file_path):
                os.remove(backup.file_path)

            # Удаляем запись из базы
            query = text("DELETE FROM backup WHERE id = :backup_id")
            await self.db.execute(query, {"backup_id": backup_id})
            await self.db.commit()

        except Exception as e:
            await self.db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Ошибка удаления бэкапа: {str(e)}"
            ) 