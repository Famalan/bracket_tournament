from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.backup import BackupService
from app.db.session import AsyncSessionLocal
from app.core.config import settings

scheduler = AsyncIOScheduler()

async def create_scheduled_backup():
    """Создание планового бэкапа"""
    async with AsyncSessionLocal() as session:
        backup_service = BackupService(session)
        try:
            await backup_service.create_backup(user_id=1)  # admin user
        except Exception as e:
            print(f"Ошибка при создании планового бэкапа: {e}")

def setup_scheduler():
    """Настройка планировщика задач"""
    # Ежедневное резервное копирование в 3:00
    scheduler.add_job(
        create_scheduled_backup,
        CronTrigger(hour=3, minute=0),
        id='daily_backup',
        replace_existing=True
    )
    
    # Еженедельное резервное копирование в вос��ресенье в 2:00
    scheduler.add_job(
        create_scheduled_backup,
        CronTrigger(day_of_week='sun', hour=2, minute=0),
        id='weekly_backup',
        replace_existing=True
    )
    
    scheduler.start() 