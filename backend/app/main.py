from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import api_router
from app.db.session import engine
from app.db.create_tables import create_tables
from app.db.init_db import init_db
import asyncio

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    # Создаем таблицы
    await create_tables(engine)
    
    # Инициализируем базу данных тестовыми данными
    from app.db.session import SessionLocal
    async with SessionLocal() as session:
        await init_db(session)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)