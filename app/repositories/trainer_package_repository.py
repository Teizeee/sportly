from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.service import TrainerPackage
from app.models.trainer import Trainer
from app.schemas.service import TrainerPackageBase

class TrainerPackageRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, trainer_package_id: str) -> Optional[TrainerPackage]:
        return self.db.query(TrainerPackage).filter(TrainerPackage.id == trainer_package_id).first()

    def get_by_gym_id(self, gym_id: str) -> List[TrainerPackage]:
        return self.db.query(TrainerPackage).filter(
            TrainerPackage.trainer.has(
                Trainer.gym_id == gym_id
            )
        ).all()
    
    def create(self, trainer_package_data: TrainerPackageBase) -> TrainerPackage:
        trainer_package = TrainerPackage(
            id=str(uuid.uuid4()),
            trainer_id=trainer_package_data.trainer_id,
            name=trainer_package_data.name,
            session_count=trainer_package_data.session_count,
            price=trainer_package_data.price,
            description=trainer_package_data.description
        )
        self.db.commit()
        self.db.refresh(trainer_package)
        return trainer_package
    
    def update(self, trainer_package: TrainerPackage, update_data: TrainerPackageBase) -> TrainerPackage:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(trainer_package, field, value)
        self.db.commit()
        self.db.refresh(trainer_package)
        return trainer_package

    def delete(self, trainer_package: TrainerPackage):
        self.db.delete(trainer_package)
        self.db.commit()