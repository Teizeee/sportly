from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.review import GymReview, TrainerReview
from app.models.user import User
from app.repositories.booking_repository import BookingRepository
from app.repositories.client_membership_repository import ClientMembershipRepository
from app.repositories.gym_repository import GymRepository
from app.repositories.review_repository import ReviewRepository
from app.repositories.trainer_repository import TrainerRepository
from app.schemas.review import (
    GymReviewAdminModel,
    GymReviewCreate,
    ReviewGymInfo,
    ReviewUserInfo,
    TrainerReviewAdminModel,
    TrainerReviewCreate
)


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.gym_repo = GymRepository(db)
        self.trainer_repo = TrainerRepository(db)
        self.client_membership_repo = ClientMembershipRepository(db)
        self.booking_repo = BookingRepository(db)
        self.review_repo = ReviewRepository(db)

    def create_gym_review(self, current_user: User, payload: GymReviewCreate) -> GymReview:
        gym = self.gym_repo.get_by_id(payload.gym_id)
        if not gym:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gym not found"
            )

        if self.review_repo.has_gym_review(current_user.id, payload.gym_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Gym review already exists"
            )

        has_active_membership = self.client_membership_repo.has_active_membership_for_gym(
            user_id=current_user.id,
            gym_id=payload.gym_id
        )
        if not has_active_membership:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only clients with active membership can leave a gym review"
            )

        return self.review_repo.create_gym_review(
            user_id=current_user.id,
            gym_id=payload.gym_id,
            rating=payload.rating,
            comment=payload.comment
        )

    def create_trainer_review(self, current_user: User, payload: TrainerReviewCreate) -> TrainerReview:
        trainer = self.trainer_repo.get_by_id(payload.trainer_id)
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )

        if self.review_repo.has_trainer_review(current_user.id, payload.trainer_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Trainer review already exists"
            )

        has_visited = self.booking_repo.has_visited_trainer(
            user_id=current_user.id,
            trainer_id=payload.trainer_id
        )
        if not has_visited:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only clients with visited bookings can leave a trainer review"
            )

        return self.review_repo.create_trainer_review(
            user_id=current_user.id,
            trainer_id=payload.trainer_id,
            rating=payload.rating,
            comment=payload.comment
        )

    def get_gym_reviews(self, gym_id: str) -> List[GymReview]:
        gym = self.gym_repo.get_by_id(gym_id)
        if not gym:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gym not found"
            )
        return self.review_repo.get_gym_reviews(gym_id)

    def get_trainer_reviews(self, trainer_id: str) -> List[TrainerReview]:
        trainer = self.trainer_repo.get_by_id(trainer_id)
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        return self.review_repo.get_trainer_reviews(trainer_id)

    def get_all_gym_reviews(self) -> List[GymReviewAdminModel]:
        reviews = self.review_repo.get_all_gym_reviews()
        return [
            GymReviewAdminModel(
                id=review.id,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
                gym=ReviewGymInfo(
                    id=review.gym.id,
                    title=review.gym.gym_application.title,
                    address=review.gym.gym_application.address
                ),
                author=ReviewUserInfo(
                    id=review.user.id,
                    first_name=review.user.first_name,
                    last_name=review.user.last_name,
                    patronymic=review.user.patronymic
                )
            )
            for review in reviews
        ]

    def get_all_trainer_reviews(self) -> List[TrainerReviewAdminModel]:
        reviews = self.review_repo.get_all_trainer_reviews()
        return [
            TrainerReviewAdminModel(
                id=review.id,
                rating=review.rating,
                comment=review.comment,
                created_at=review.created_at,
                gym=ReviewGymInfo(
                    id=review.trainer.gym.id,
                    title=review.trainer.gym.gym_application.title,
                    address=review.trainer.gym.gym_application.address
                ),
                trainer=ReviewUserInfo(
                    id=review.trainer.user.id,
                    first_name=review.trainer.user.first_name,
                    last_name=review.trainer.user.last_name,
                    patronymic=review.trainer.user.patronymic
                ),
                author=ReviewUserInfo(
                    id=review.user.id,
                    first_name=review.user.first_name,
                    last_name=review.user.last_name,
                    patronymic=review.user.patronymic
                )
            )
            for review in reviews
        ]

    def delete_gym_review(self, review_id: str):
        review = self.review_repo.get_gym_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Gym review not found"
            )
        self.review_repo.soft_delete_gym_review(review)

    def delete_trainer_review(self, review_id: str):
        review = self.review_repo.get_trainer_review_by_id(review_id)
        if not review:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer review not found"
            )
        self.review_repo.soft_delete_trainer_review(review)
