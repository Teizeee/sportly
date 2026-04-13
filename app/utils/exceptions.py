from fastapi import HTTPException, status
from typing import Optional, Any


class AuthException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: Any = None,
        headers: Optional[dict[str, str]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class UserNotFoundException(AuthException):
    def __init__(self, user_id: Optional[str] = None):
        detail = f"Пользователь не найден" + (f": {user_id}" if user_id else "")
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class UserAlreadyExistsException(AuthException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Пользователь с email {email} уже существует"
        )


class InvalidCredentialsException(AuthException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные учетные данные",
            headers={"WWW-Authenticate": "Bearer"}
        )


class UserBlockedException(AuthException):
    def __init__(self, reason: Optional[str] = None):
        detail = f"Пользователь заблокирован" + (f": {reason}" if reason else "")
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)


class PermissionDeniedException(AuthException):
    def __init__(self, message: str = "Доступ запрещен"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)