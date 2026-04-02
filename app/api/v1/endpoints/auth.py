from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.schemas.user import (
    GetUserTrainerWithPassword, UserCreate, UserLogin,
    TokenResponse, UserUpdate, UserBlock, PasswordChange
)
from app.schemas.user_profile import UserResponse
from app.services.auth_service import AuthService
from app.models.user import User, UserRole

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED, response_model_exclude_none=True)
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
    subsystem: str = Header(..., alias="Subsystem"),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.login(login_data, subsystem)


@router.get("/me", response_model=UserResponse, response_model_exclude_none=True)
async def get_current_user_info(
    current_user: User = Depends(dependencies.get_current_active_user)
):
    return current_user


@router.put("/me", response_model=UserResponse, response_model_exclude_none=True)
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


@router.get("/users", response_model=List[GetUserTrainerWithPassword], response_model_exclude_none=True)
async def get_users(
    gym_id: Optional[str] = Query(None, description="Filter users by gym"),
    role: Optional[UserRole] = Query(None, description="Filter users by role"),
    include_blocked: Optional[bool] = Query(None, description="Filter blocked users"),
    current_user: User = Depends(dependencies.require_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.get_users(current_user, gym_id, role, include_blocked)


@router.get("/users/count")
async def users_count(
    _: User = Depends(dependencies.require_super_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.users_count()


@router.post("/users/{user_id}/block", response_model=UserResponse, response_model_exclude_none=True)
async def block_user(
    user_id: str,
    block_data: UserBlock,
    current_user: User = Depends(dependencies.require_super_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.block_user(current_user.id, user_id, block_data)


@router.post("/users/{user_id}/unblock", response_model=UserResponse, response_model_exclude_none=True)
async def unblock_user(
    user_id: str,
    current_user: User = Depends(dependencies.require_super_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.unblock_user(current_user.id, user_id)


@router.put("/users/{user_id}", response_model=UserResponse, response_model_exclude_none=True)
async def update_profile(
    user_id: str,
    update_data: UserUpdate,
    _: User = Depends(dependencies.require_super_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    return auth_service.update_profile(user_id, update_data)


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(dependencies.require_admin),
    db: Session = Depends(get_db)
):
    auth_service = AuthService(db)
    auth_service.delete_user(current_user.id, user_id)
    return {"message": "User deleted successfully"}
