from datetime import date
from typing import List

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service import (
    ClientMembership,
    ClientMembershipStatus,
    UserTrainerPackage,
    UserTrainerPackageStatus
)
from app.models.user import User
from app.repositories.client_membership_repository import ClientMembershipRepository
from app.repositories.membership_type_repository import MembershipTypeRepository
from app.repositories.trainer_package_repository import TrainerPackageRepository
from app.repositories.user_repository import UserRepository
from app.repositories.user_trainer_package_repository import UserTrainerPackageRepository
from app.schemas.service import (
    ActiveClientServicesModel,
    ClientMembershipCreate,
    UserTrainerPackageCreate
)


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

    def get_my_memberships(self, current_user: User) -> List[ClientMembership]:
        return self.client_membership_repo.get_by_user_id_ordered(current_user.id)

    def get_my_trainer_packages(self, current_user: User) -> List[UserTrainerPackage]:
        return self.user_trainer_package_repo.get_by_user_id_ordered(current_user.id)

    def get_my_active_services(self, current_user: User) -> ActiveClientServicesModel:
        active_membership = self.client_membership_repo.get_active_by_user_id(current_user.id)
        active_package = self.user_trainer_package_repo.get_active_by_user_id(current_user.id)
        return ActiveClientServicesModel(
            active_membership=active_membership,
            active_package=active_package
        )

    def activate_my_membership(self, current_user: User, membership_id: str) -> ClientMembership:
        membership = self.client_membership_repo.get_by_id(membership_id)
        if not membership or membership.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Membership not found"
            )

        if membership.status == ClientMembershipStatus.EXPIRED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Expired membership cannot be activated"
            )

        active_membership = self.client_membership_repo.get_active_by_user_id(current_user.id)
        if active_membership and active_membership.id != membership.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active membership"
            )

        if membership.status == ClientMembershipStatus.ACTIVE:
            return membership

        activated_at = date.today()
        expires_at = activated_at + relativedelta(months=membership.membership_type.duration_months)
        return self.client_membership_repo.activate(membership, activated_at, expires_at)

    def activate_my_trainer_package(self, current_user: User, user_trainer_package_id: str) -> UserTrainerPackage:
        user_trainer_package = self.user_trainer_package_repo.get_by_id(user_trainer_package_id)
        if not user_trainer_package or user_trainer_package.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer package not found"
            )

        if user_trainer_package.status == UserTrainerPackageStatus.FINISHED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Finished trainer package cannot be activated"
            )

        active_package = self.user_trainer_package_repo.get_active_by_user_id(current_user.id)
        if active_package and active_package.id != user_trainer_package.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User already has an active trainer package"
            )

        if user_trainer_package.status == UserTrainerPackageStatus.ACTIVE:
            return user_trainer_package

        return self.user_trainer_package_repo.activate(user_trainer_package, date.today())

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
