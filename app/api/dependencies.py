from fastapi import Depends, HTTPException, Header, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_token
from app.schemas.user import TokenData
from app.services.auth_service import AuthService
from app.models.user import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_token(token)
    user_id: str = payload.get("sub")

    if user_id is None:
        raise credentials_exception

    token_data = TokenData(user_id=user_id, role=payload.get("role"))

    auth_service = AuthService(db)
    user = auth_service.get_current_user(token_data.user_id)

    if user is None:
        raise credentials_exception

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    if current_user.is_blocked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User is blocked. Reason: {current_user.blocked_comment or 'No reason provided'}"
        )

    return current_user


async def get_current_user_optional(
        authorization: Optional[str] = Header(None, alias="Authorization"),
        db: Session = Depends(get_db)
) -> Optional[User]:
    if authorization is None:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
    except ValueError:
        return None
    
    try:
        payload = decode_token(token)
        user_id: str = payload.get("sub")
        
        if user_id is None:
            return None
            
        auth_service = AuthService(db)
        user = auth_service.get_current_user(user_id)
        
        if user and user.is_blocked:
            return None
            
        return user
    except JWTError:
        return None
    except Exception:
        return None

def require_roles(allowed_roles: list[UserRole]):
    async def role_checker(current_user: User = Depends(get_current_active_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires one of these roles: {[r.value for r in allowed_roles]}"
            )
        return current_user

    return role_checker


require_admin = require_roles([UserRole.GYM_ADMIN, UserRole.SUPER_ADMIN])
require_gym_admin = require_roles([UserRole.GYM_ADMIN])
require_super_admin = require_roles([UserRole.SUPER_ADMIN])