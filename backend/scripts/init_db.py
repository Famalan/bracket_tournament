import asyncio
import sys
import os

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import AsyncSessionLocal
from app.db.init_db import init_db

async def main() -> None:
    async with AsyncSessionLocal() as session:
        await init_db(session)

if __name__ == "__main__":
    asyncio.run(main()) 