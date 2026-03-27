from datetime import date
import uuid

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
