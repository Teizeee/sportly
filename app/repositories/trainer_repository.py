from typing import Optional

from sqlalchemy.orm import Session

from app.models.trainer import Trainer


class TrainerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, trainer_id: str) -> Optional[Trainer]:
        return self.db.query(Trainer).filter(Trainer.id == trainer_id).first()