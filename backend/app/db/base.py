from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import Any, Dict, List

class DatabaseService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def execute_query(
        self, 
        query: str, 
        params: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Выполнение параметризованного SQL-запроса"""
        try:
            result = await self.session.execute(text(query), params)
            await self.session.commit()
            return [dict(row) for row in result]
        except Exception as e:
            await self.session.rollback()
            raise DatabaseError(f"Ошибка выполнения запроса: {str(e)}") 