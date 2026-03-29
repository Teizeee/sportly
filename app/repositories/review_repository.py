import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.review import GymReview, TrainerReview
from app.models.gym import Gym, GymApplication
from app.models.trainer import Trainer


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def has_gym_review(self, user_id: str, gym_id: str) -> bool:
        return self.db.query(GymReview).filter(
            GymReview.user_id == user_id,
            GymReview.gym_id == gym_id,
            GymReview.deleted_at.is_(None)
        ).first() is not None

    def has_trainer_review(self, user_id: str, trainer_id: str) -> bool:
        return self.db.query(TrainerReview).filter(
            TrainerReview.user_id == user_id,
            TrainerReview.trainer_id == trainer_id,
            TrainerReview.deleted_at.is_(None)
        ).first() is not None

    def create_gym_review(
        self,
        user_id: str,
        gym_id: str,
        rating: int,
        comment: Optional[str]
    ) -> GymReview:
        review = GymReview(
            id=str(uuid.uuid4()),
            user_id=user_id,
            gym_id=gym_id,
            rating=rating,
            comment=comment
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def create_trainer_review(
        self,
        user_id: str,
        trainer_id: str,
        rating: int,
        comment: Optional[str]
    ) -> TrainerReview:
        review = TrainerReview(
            id=str(uuid.uuid4()),
            user_id=user_id,
            trainer_id=trainer_id,
            rating=rating,
            comment=comment
        )
        self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return review

    def get_gym_reviews(self, gym_id: str) -> List[GymReview]:
        return self.db.query(GymReview).filter(
            GymReview.gym_id == gym_id,
            GymReview.deleted_at.is_(None)
        ).order_by(
            GymReview.created_at.desc()
        ).all()

    def get_trainer_reviews(self, trainer_id: str) -> List[TrainerReview]:
        return self.db.query(TrainerReview).filter(
            TrainerReview.trainer_id == trainer_id,
            TrainerReview.deleted_at.is_(None)
        ).order_by(
            TrainerReview.created_at.desc()
        ).all()

    def get_all_gym_reviews(self) -> List[GymReview]:
        return self.db.query(GymReview).options(
            joinedload(GymReview.user),
            joinedload(GymReview.gym).joinedload(Gym.gym_application)
        ).filter(
            GymReview.deleted_at.is_(None)
        ).order_by(
            GymReview.created_at.desc()
        ).all()

    def get_all_trainer_reviews(self) -> List[TrainerReview]:
        return self.db.query(TrainerReview).options(
            joinedload(TrainerReview.user),
            joinedload(TrainerReview.trainer).joinedload(Trainer.user),
            joinedload(TrainerReview.trainer).joinedload(Trainer.gym).joinedload(Gym.gym_application)
        ).filter(
            TrainerReview.deleted_at.is_(None)
        ).order_by(
            TrainerReview.created_at.desc()
        ).all()

    def get_gym_review_by_id(self, review_id: str) -> Optional[GymReview]:
        return self.db.query(GymReview).filter(
            GymReview.id == review_id,
            GymReview.deleted_at.is_(None)
        ).first()

    def get_trainer_review_by_id(self, review_id: str) -> Optional[TrainerReview]:
        return self.db.query(TrainerReview).filter(
            TrainerReview.id == review_id,
            TrainerReview.deleted_at.is_(None)
        ).first()

    def soft_delete_gym_review(self, review: GymReview):
        review.deleted_at = datetime.utcnow()
        self.db.commit()

    def soft_delete_trainer_review(self, review: TrainerReview):
        review.deleted_at = datetime.utcnow()
        self.db.commit()
