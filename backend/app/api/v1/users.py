import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from typing import List
from app.db.session import get_db
from app.schemas.user import UserCreate, UserResponse, UserUpdate, UserRoleUpdate
from app.core.security import get_current_user, get_password_hash
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение списка пользователей (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    query = text("""
        SELECT id, username, email, role, created_at, updated_at
        FROM users
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :skip
    """)
    
    result = await db.execute(query, {"limit": limit, "skip": skip})
    return result.fetchall()

@router.post("/", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Создание нового пользователя (только для админов)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    hashed_password = get_password_hash(user.password)
    
    query = text("""
        INSERT INTO users (username, email, hashed_password, role, is_active)
        VALUES (:username, :email, :hashed_password, :role, :is_active)
        RETURNING id, username, email, role, is_active, created_at, updated_at
    """)
    
    try:
        result = await db.execute(
            query,
            {
                "username": user.username,
                "email": user.email,
                "hashed_password": hashed_password,
                "role": user.role,
                "is_active": True
            }
        )
        await db.commit()
        return result.fetchone()
    except Exception as e:
        logger.error(f"Ошибка при создании пользователя: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Пользователь с таким именем или email уже существует"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Получение информации о пользователе"""
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    query = text("""
        SELECT id, username, email, role, created_at, updated_at
        FROM users
        WHERE id = :user_id
    """)
    
    result = await db.execute(query, {"user_id": user_id})
    user = result.fetchone()
    
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление информации о пользователе"""
    if current_user["role"] != "admin" and current_user["id"] != user_id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    update_data = user_update.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    set_values = ", ".join(f"{k} = :{k}" for k in update_data.keys())
    
    query = text(f"""
        UPDATE users
        SET {set_values}
        WHERE id = :user_id
        RETURNING id, username, email, role, is_active, created_at, updated_at
    """)
    
    try:
        result = await db.execute(query, {**update_data, "user_id": user_id})
        await db.commit()
        updated_user = result.fetchone()
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return updated_user
    except Exception as e:
        logger.error(f"Ошибка при обновлении пользователя: {e}")
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка обновления пользователя")

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Удаление пользователя (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    # Проверяем, не пытается ли админ удалить самого себя
    if current_user.id == user_id:
        raise HTTPException(
            status_code=400, 
            detail="Невозможно удалить свою учетную запись"
        )
    
    query = text("DELETE FROM users WHERE id = :user_id")
    
    try:
        result = await db.execute(query, {"user_id": user_id})
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
    except Exception as e:
        logger.error(f"Ошибка при удалении пользователя: {e}")
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка удаления пользователя")

@router.patch("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserRoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Обновление роли пользователя (только для админов)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    
    query = text("""
        UPDATE users
        SET role = :role
        WHERE id = :user_id
        RETURNING id, username, email, role, created_at, updated_at
    """)
    
    try:
        result = await db.execute(
            query, 
            {
                "user_id": user_id, 
                "role": role_update.role.value
            }
        )
        await db.commit()
        updated_user = result.fetchone()
        if not updated_user:
            raise HTTPException(status_code=404, detail="Пользователь не найден")
        return updated_user
    except Exception as e:
        logger.error(f"Ошибка при обновлении роли пользователя: {e}")
        await db.rollback()
        raise HTTPException(status_code=400, detail="Ошибка обновления роли пользователя")