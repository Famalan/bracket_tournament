from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

async def check_tables(db: AsyncSession) -> dict:
    try:
        # Проверяем существование таблиц
        tables_query = text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        result = await db.execute(tables_query)
        existing_tables = [row[0] for row in result.fetchall()]
        
        return {
            "tables_exist": all(table in existing_tables 
                              for table in ['users', 'teams', 'players']),
            "existing_tables": existing_tables
        }
    except Exception as e:
        print(f"Ошибка при проверке таблиц: {e}")
        return {"error": str(e)} 