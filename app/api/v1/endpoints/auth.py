from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.schemas.user import (
    UserCreate, UserLogin, UserResponse,
    TokenResponse, UserUpdate, UserBlock, PasswordChange
)
from app.services.auth_service import AuthService
from app.models.user import User

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(dependencies.get_current_user_optional)
):
    auth_service = AuthService(db)
    user = auth_service.register(current_user, user_data)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.login(login_data)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(dependencies.get_current_active_user)
):
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.update_profile(current_user.id, update_data)


@router.patch("/me/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    auth_service.change_password(current_user.id, password_data)
    return {"message": "Password changed successfully"}


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_own_account(
    current_user: User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    auth_service.delete_user(current_user.id, current_user.id)
    return None


@router.post("/users/{user_id}/block", response_model=UserResponse)
async def block_user(
    user_id: str,
    block_data: UserBlock,
    current_user: User = Depends(dependencies.require_super_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.block_user(current_user.id, user_id, block_data)


@router.post("/users/{user_id}/unblock", response_model=UserResponse)
async def unblock_user(
    user_id: str,
    current_user: User = Depends(dependencies.require_super_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.unblock_user(current_user.id, user_id)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(dependencies.require_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    auth_service.delete_user(current_user.id, user_id)
    return {"message": "User deleted successfully"}