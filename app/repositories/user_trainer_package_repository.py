from datetime import date
import uuid
from typing import List, Optional

from sqlalchemy import case
from sqlalchemy.orm import Session

from app.models.service import UserTrainerPackage, UserTrainerPackageStatus


class UserTrainerPackageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, trainer_package_id: str, sessions_left: int) -> UserTrainerPackage:
        user_trainer_package = UserTrainerPackage(
            id=str(uuid.uuid4()),
            user_id=user_id,
            trainer_package_id=trainer_package_id,
            status=UserTrainerPackageStatus.PURCHASED,
            sessions_left=sessions_left,
            purchased_at=date.today(),
            activated_at=None,
            expires_at=None
        )
        self.db.add(user_trainer_package)
        self.db.commit()
        self.db.refresh(user_trainer_package)
        return user_trainer_package

    def get_by_id(self, user_trainer_package_id: str) -> Optional[UserTrainerPackage]:
        return self.db.query(UserTrainerPackage).filter(
            UserTrainerPackage.id == user_trainer_package_id
        ).first()

    def get_by_user_id_ordered(self, user_id: str) -> List[UserTrainerPackage]:
        status_order = case(
            (UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE, 0),
            (UserTrainerPackage.status == UserTrainerPackageStatus.PURCHASED, 1),
            else_=2
        )
        return self.db.query(UserTrainerPackage).filter(
            UserTrainerPackage.user_id == user_id
        ).order_by(
            status_order.asc(),
            UserTrainerPackage.purchased_at.desc()
        ).all()

    def get_active_by_user_id(self, user_id: str) -> Optional[UserTrainerPackage]:
        return self.db.query(UserTrainerPackage).filter(
            UserTrainerPackage.user_id == user_id,
            UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE
        ).order_by(
            UserTrainerPackage.activated_at.desc()
        ).first()

    def activate(self, user_trainer_package: UserTrainerPackage, activated_at: date) -> UserTrainerPackage:
        user_trainer_package.status = UserTrainerPackageStatus.ACTIVE
        user_trainer_package.activated_at = activated_at
        self.db.commit()
        self.db.refresh(user_trainer_package)
        return user_trainer_package
