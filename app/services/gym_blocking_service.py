from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.gym import GymBlocking
from app.models.user import User
from app.repositories.gym_blocking_repository import GymBlockingRepository
from app.repositories.user_repository import UserRepository


class GymBlockingService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.gym_blocking_repo = GymBlockingRepository(db)

    def block_user(self, current_user: User, gym_id: str, user_id: str, comment: Optional[str] = None) -> GymBlocking:
        self._validate_access(current_user, gym_id)

        if current_user.id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot block yourself"
            )

        user_to_block = self.user_repo.get_by_id(user_id)
        if not user_to_block:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        if user_to_block.role != "CLIENT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CLIENT can be blocked by gym admin"
            )

        if not self._user_belongs_to_gym(gym_id, user_to_block):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User does not belong to this gym"
            )

        existing_blocking = self.gym_blocking_repo.get_by_gym_and_user_id(gym_id, user_id)
        if existing_blocking:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already blocked in this gym"
            )

        return self.gym_blocking_repo.create(gym_id, user_id, comment)

    def unblock_user(self, current_user: User, gym_id: str, user_id: str) -> None:
        self._validate_access(current_user, gym_id)

        blocking = self.gym_blocking_repo.get_by_gym_and_user_id(gym_id, user_id)
        if not blocking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User is not blocked in this gym"
            )

        self.gym_blocking_repo.delete(blocking)

    def _validate_access(self, current_user: User, gym_id: str) -> None:
        if not current_user.gym or current_user.gym.id != gym_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

    def _user_belongs_to_gym(self, gym_id: str, user: User) -> bool:
        if user.role == "CLIENT":
            return self.gym_blocking_repo.is_client_of_gym(gym_id, user.id)
        return False
