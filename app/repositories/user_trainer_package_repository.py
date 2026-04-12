from datetime import date
import uuid
from typing import Dict, List, Optional

from dateutil.relativedelta import relativedelta
from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload

from app.models.service import TrainerPackage, UserTrainerPackage, UserTrainerPackageStatus
from app.models.trainer import Trainer


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
            activated_at=None
        )
        self.db.add(user_trainer_package)
        self.db.commit()
        self.db.refresh(user_trainer_package)
        return user_trainer_package

    def get_by_id(self, user_trainer_package_id: str) -> Optional[UserTrainerPackage]:
        return self.db.query(UserTrainerPackage).options(
            joinedload(UserTrainerPackage.trainer_package)
            .joinedload(TrainerPackage.trainer)
            .joinedload(Trainer.user)
        ).filter(
            UserTrainerPackage.id == user_trainer_package_id
        ).first()

    def get_by_id_for_update(self, user_trainer_package_id: str) -> Optional[UserTrainerPackage]:
        return self.db.query(UserTrainerPackage).filter(
            UserTrainerPackage.id == user_trainer_package_id
        ).with_for_update().first()

    def get_by_user_id_ordered(self, user_id: str) -> List[UserTrainerPackage]:
        status_order = case(
            (UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE, 0),
            (UserTrainerPackage.status == UserTrainerPackageStatus.PURCHASED, 1),
            else_=2
        )
        return self.db.query(UserTrainerPackage).options(
            joinedload(UserTrainerPackage.trainer_package)
            .joinedload(TrainerPackage.trainer)
            .joinedload(Trainer.user)
        ).filter(
            UserTrainerPackage.user_id == user_id
        ).order_by(
            status_order.asc(),
            UserTrainerPackage.purchased_at.desc()
        ).all()

    def get_active_by_user_id(self, user_id: str) -> Optional[UserTrainerPackage]:
        return self.db.query(UserTrainerPackage).options(
            joinedload(UserTrainerPackage.trainer_package)
            .joinedload(TrainerPackage.trainer)
            .joinedload(Trainer.user)
        ).filter(
            UserTrainerPackage.user_id == user_id,
            UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE
        ).order_by(
            UserTrainerPackage.activated_at.desc()
        ).first()

    def get_active_by_user_ids_for_gym(
        self,
        user_ids: List[str],
        gym_id: str
    ) -> Dict[str, UserTrainerPackage]:
        if not user_ids:
            return {}

        active_packages = self.db.query(UserTrainerPackage).join(
            TrainerPackage, TrainerPackage.id == UserTrainerPackage.trainer_package_id
        ).join(
            Trainer, Trainer.id == TrainerPackage.trainer_id
        ).options(
            joinedload(UserTrainerPackage.trainer_package)
            .joinedload(TrainerPackage.trainer)
            .joinedload(Trainer.user)
        ).filter(
            UserTrainerPackage.user_id.in_(user_ids),
            UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE,
            Trainer.gym_id == gym_id
        ).order_by(
            UserTrainerPackage.user_id.asc(),
            UserTrainerPackage.activated_at.desc()
        ).all()

        result: Dict[str, UserTrainerPackage] = {}
        for package in active_packages:
            if package.user_id not in result:
                result[package.user_id] = package
        return result

    def get_active_by_user_id_for_update(self, user_id: str) -> Optional[UserTrainerPackage]:
        return self.db.query(UserTrainerPackage).filter(
            UserTrainerPackage.user_id == user_id,
            UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE
        ).order_by(
            UserTrainerPackage.activated_at.desc()
        ).with_for_update().first()

    def activate(self, user_trainer_package: UserTrainerPackage, activated_at: date) -> UserTrainerPackage:
        user_trainer_package.status = UserTrainerPackageStatus.ACTIVE
        user_trainer_package.activated_at = activated_at
        self.db.commit()
        self.db.refresh(user_trainer_package)
        return user_trainer_package

    def finish_expired_active_packages(self, today: Optional[date] = None) -> int:
        return self._finish_expired_active_query(
            self.db.query(UserTrainerPackage).filter(
                UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE,
                UserTrainerPackage.activated_at.isnot(None)
            ),
            today=today
        )

    def finish_expired_active_packages_for_user(self, user_id: str, today: Optional[date] = None) -> int:
        return self._finish_expired_active_query(
            self.db.query(UserTrainerPackage).filter(
                UserTrainerPackage.user_id == user_id,
                UserTrainerPackage.status == UserTrainerPackageStatus.ACTIVE,
                UserTrainerPackage.activated_at.isnot(None)
            ),
            today=today
        )

    def _finish_expired_active_query(self, query, today: Optional[date] = None) -> int:
        current_date = today or date.today()
        updated = 0

        for user_trainer_package in query.all():
            if user_trainer_package.activated_at + relativedelta(months=1) <= current_date:
                user_trainer_package.status = UserTrainerPackageStatus.FINISHED
                updated += 1

        if updated:
            self.db.commit()

        return updated
