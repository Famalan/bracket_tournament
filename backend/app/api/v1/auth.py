from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db.session import get_db
from app.core.security import create_access_token, verify_password, get_current_user, get_password_hash
from app.core.config import settings
from app.models.user import User, UserRole
from sqlalchemy import select, insert
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Поиск пользователя
    query = text("""
        SELECT id, username, hashed_password, role 
        FROM users 
        WHERE username = :username
    """)
    
    result = await db.execute(query, {"username": form_data.username})
    user = result.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    # Проверка пароля
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверное имя пользователя или пароль"
        )

    # Создание токена
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role},
        expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }

@router.post("/register")
async def register(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    try:
        # Проверяем существование пользователя
        query = text("""
            SELECT id FROM users 
            WHERE username = :username
        """)
        result = await db.execute(query, {"username": form_data.username})
        if result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )

        # Создаем нового пользователя
        hashed_password = get_password_hash(form_data.password)
        
        # Генерируем временный email
        temp_email = f"{form_data.username}@example.com"
        
        stmt = insert(User).values(
            username=form_data.username,
            email=temp_email,  # Добавляем временный email
            hashed_password=hashed_password,
            role=UserRole.PLAYER,
            is_active=True
        ).returning(User)
        
        result = await db.execute(stmt)
        user = result.scalar_one()
        await db.commit()

        # Создаем токен доступа
        access_token = create_access_token(data={"sub": str(user.id)})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role.value
            }
        }
    except Exception as e:
        logger.error(f"Ошибка при регистрации: {str(e)}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/me", response_model=dict)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "role": current_user.role
        }
    }