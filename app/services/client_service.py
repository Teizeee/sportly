from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.client_membership_repository import ClientMembershipRepository
from app.repositories.membership_type_repository import MembershipTypeRepository
from app.repositories.trainer_package_repository import TrainerPackageRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_trainer_package_repository import UserTrainerPackageRepository
from app.schemas.service import ClientMembershipCreate, UserTrainerPackageCreate


class ClientService:
    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)
        self.membership_type_repo = MembershipTypeRepository(db)
        self.trainer_package_repo = TrainerPackageRepository(db)
        self.client_membership_repo = ClientMembershipRepository(db)
        self.user_trainer_package_repo = UserTrainerPackageRepository(db)

    def create_client_membership(
        self,
        current_user: User,
        membership_data: ClientMembershipCreate
    ):
        self._validate_current_user_gym(current_user)
        client = self._get_client_or_404(membership_data.user_id)

        membership_type = self.membership_type_repo.get_by_id(membership_data.membership_type_id)
        if not membership_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership type not found"
            )
        if membership_type.gym_id != current_user.gym.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return self.client_membership_repo.create(
            user_id=client.id,
            membership_type_id=membership_type.id
        )

    def create_user_trainer_package(
        self,
        current_user: User,
        package_data: UserTrainerPackageCreate
    ):
        self._validate_current_user_gym(current_user)
        client = self._get_client_or_404(package_data.user_id)

        trainer_package = self.trainer_package_repo.get_by_id(package_data.trainer_package_id)
        if not trainer_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer package not found"
            )
        if trainer_package.trainer.gym_id != current_user.gym.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return self.user_trainer_package_repo.create(
            user_id=client.id,
            trainer_package_id=trainer_package.id,
            sessions_left=trainer_package.session_count
        )

    def _get_client_or_404(self, user_id: str) -> User:
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        if user.role != "CLIENT":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CLIENT can be assigned to services"
            )
        return user

    @staticmethod
    def _validate_current_user_gym(current_user: User):
        if not current_user.gym:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Gym admin has no approved gym"
            )
