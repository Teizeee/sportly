from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.service import MembershipType, TrainerPackage
from app.models.user import User
from app.repositories.membership_type_repository import MembershipTypeRepository
from app.repositories.trainer_package_repository import TrainerPackageRepository
from app.repositories.trainer_repository import TrainerRepository
from app.schemas.service import MembershipTypeBase, TrainerPackageBase


class ServicesService:
    def __init__(self, db: Session):
        self.db = db
        self.membership_type_repo = MembershipTypeRepository(db)
        self.trainer_package_repo = TrainerPackageRepository(db)
        self.trainer_repo = TrainerRepository(db)

    # Членства (абонементы)

    def get_membership_types(self, gym_id: str) -> List[MembershipType]:
        return self.membership_type_repo.get_by_gym_id(gym_id)
    
    def create_membership_type(self, current_user: User, membership_type_data: MembershipTypeBase) -> MembershipType:
        return self.membership_type_repo.create(current_user.gym.id, membership_type_data)
    
    def update_membership_type(self, current_user: User, membership_type_id: str, membership_type_data: MembershipTypeBase) -> MembershipType:
        membership_type = self.membership_type_repo.get_by_id(membership_type_id)
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
        return self.membership_type_repo.update(membership_type, membership_type_data)
    
    def delete_membership_type(self, current_user: User, membership_type_id: str):
        membership_type = self.membership_type_repo.get_by_id(membership_type_id)
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
        self.membership_type_repo.delete(membership_type)

    # Пакеты с тренерами

    def get_trainer_packages(self, gym_id: str) -> List[TrainerPackage]:
        return self.trainer_package_repo.get_by_gym_id(gym_id)
    
    def create_trainer_package(self, current_user: User, trainer_package_data: TrainerPackageBase) -> TrainerPackage:
        trainer = self.trainer_repo.get_by_id(trainer_package_data.trainer_id)
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        if trainer.gym_id != current_user.gym.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        return self.trainer_package_repo.create(trainer_package_data)
    
    def update_trainer_package(self, current_user: User, trainer_package_id: str, trainer_package_data: TrainerPackageBase) -> TrainerPackage:
        trainer_package = self.trainer_package_repo.get_by_id(trainer_package_id)
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
        return self.trainer_package_repo.update(trainer_package, trainer_package_data)
    
    def delete_trainer_package(self, current_user: User, trainer_package_id: str):
        trainer_package = self.trainer_package_repo.get_by_id(trainer_package_id)
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
        self.trainer_package_repo.delete(trainer_package)