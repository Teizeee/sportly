from typing import Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.review import TrainerReview
from app.models.trainer import Trainer
from app.models.user import User


class TrainerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, trainer_id: str) -> Optional[Trainer]:
        return self.db.query(Trainer).filter(Trainer.id == trainer_id).first()

    def get_by_gym_id(self, gym_id: str) -> List[Trainer]:
        return (
            self.db.query(Trainer)
            .join(User, User.id == Trainer.user_id)
            .filter(
                Trainer.gym_id == gym_id,
                User.deleted_at.is_(None),
            )
            .all()
        )

    def get_trainers_ratings(self, trainer_ids: List[str]) -> Dict[str, float]:
        if not trainer_ids:
            return {}

        rows = (
            self.db.query(
                TrainerReview.trainer_id,
                func.avg(TrainerReview.rating).label("avg_rating"),
            )
            .filter(
                TrainerReview.trainer_id.in_(trainer_ids),
                TrainerReview.deleted_at.is_(None),
            )
            .group_by(TrainerReview.trainer_id)
            .all()
        )

        return {
            trainer_id: float(avg_rating)
            for trainer_id, avg_rating in rows
            if avg_rating is not None
        }
