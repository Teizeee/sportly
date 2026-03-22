from typing import List

from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate, UserLogin, UserUpdate, UserBlock, PasswordChange, UsersCount
from app.core.security import verify_password, get_password_hash, create_access_token
from app.models.user import User, UserRole


class AuthService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register(self, current_user: User, user_data: UserCreate) -> User:
        existing_user = self.user_repo.get_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        if user_data.role == "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User can not register as SUPER_ADMIN by himself"
            )
        if user_data.role == "TRAINER":
            if current_user is not None and current_user.role == "GYM_ADMIN":
                user_data.gym_id = current_user.gym.id
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User can only be registered as TRAINER by gym admin"
                )
            

        hashed_password = get_password_hash(user_data.password)
        user = self.user_repo.create(user_data, hashed_password)

        return user

    def login(self, login_data: UserLogin) -> dict:
        user = self.user_repo.get_by_email(login_data.email)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account has been deleted"
            )

        if user.is_blocked:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Account is blocked. Reason: {user.blocked_comment or 'No reason provided'}"
            )

        if not verify_password(login_data.password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        access_token = create_access_token(
            subject=user.id,
            role=user.role.value
        )

        return {
            "access_token": access_token,
            "token_type": "bearer"
        }

    def get_current_user(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account has been deleted"
            )

        return user
    
    def get_users(self, current_user: User, gym_id: str, role: UserRole) -> List[User]:
        if current_user.role == "GYM_ADMIN":
            if current_user.gym.id != gym_id or role in ["GYM_ADMIN", "SUPER_ADMIN"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )

        return self.user_repo.get_all(
            gym_id, role
        )
    
    def users_count(self) -> UsersCount:
        stats = self.user_repo.get_count()
        return UsersCount(
            total=stats.total,
            clients=stats.clients,
            trainers=stats.trainers,
            gym_admins=stats.gym_admins
        )

    def update_profile(self, user_id: str, update_data: UserUpdate) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        existing_user = self.user_repo.get_by_email(update_data.email)
        if existing_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )

        return self.user_repo.update(user, update_data)

    def change_password(self, user_id: str, password_data: PasswordChange) -> bool:
        user = self.get_current_user(user_id)

        if not verify_password(password_data.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        hashed_password = get_password_hash(password_data.new_password)
        self.user_repo.update_password(user, hashed_password)

        return True

    def block_user(self, admin_id: str, target_user_id: str, block_data: UserBlock) -> User:
        if admin_id == target_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot block a super admin"
            )

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return self.user_repo.block(target_user, block_data)

    def unblock_user(self, admin_id: str, target_user_id: str) -> User:
        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        return self.user_repo.unblock(target_user)

    def delete_user(self, user_id: str, target_user_id: str) -> bool:
        current_user = self.get_current_user(user_id)

        if user_id == target_user_id and current_user.role == "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete a super admin"
            )

        target_user = self.user_repo.get_by_id(target_user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if current_user.role == "GYM_ADMIN" and target_user.role == "TRAINER" and target_user.trainer_profile.gym_id == current_user.gym.id:
            self.user_repo.delete(target_user)
            return True

        if user_id != target_user_id and current_user.role != "SUPER_ADMIN":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to delete other users"
            )

        self.user_repo.delete(target_user)
        return True