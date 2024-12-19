from fastapi import HTTPException, status
from typing import Optional

class TournamentException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = "Ошибка в турнире"
    ):
        super().__init__(status_code=status_code, detail=detail)

class NotFoundError(TournamentException):
    def __init__(self, entity: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{entity} не найден"
        )

class PermissionError(TournamentException):
    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message
        )

class ValidationError(TournamentException):
    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message
        )

class DatabaseError(TournamentException):
    def __init__(self, detail: str = "Ошибка базы данных"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )

class AuthenticationError(TournamentException):
    def __init__(self, detail: str = "Ошибка аутентификации"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail
        ) 