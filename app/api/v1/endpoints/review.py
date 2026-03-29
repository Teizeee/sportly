from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.review import (
    GymReviewAdminModel,
    GymReviewCreate,
    GymReviewModel,
    TrainerReviewAdminModel,
    TrainerReviewCreate,
    TrainerReviewModel
)
from app.services.review_service import ReviewService

router = APIRouter()


@router.get(
    "/gyms/{gym_id}/reviews",
    response_model=List[GymReviewModel],
    status_code=status.HTTP_200_OK
)
async def get_gym_reviews(
    gym_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.get_current_active_user)
):
    review_service = ReviewService(db)
    return review_service.get_gym_reviews(gym_id)


@router.get(
    "/trainers/{trainer_id}/reviews",
    response_model=List[TrainerReviewModel],
    status_code=status.HTTP_200_OK
)
async def get_trainer_reviews(
    trainer_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.get_current_active_user)
):
    review_service = ReviewService(db)
    return review_service.get_trainer_reviews(trainer_id)


@router.get(
    "/admin/reviews/gyms",
    response_model=List[GymReviewAdminModel],
    status_code=status.HTTP_200_OK
)
async def get_all_gym_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    review_service = ReviewService(db)
    return review_service.get_all_gym_reviews()


@router.get(
    "/admin/reviews/trainers",
    response_model=List[TrainerReviewAdminModel],
    status_code=status.HTTP_200_OK
)
async def get_all_trainer_reviews(
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    review_service = ReviewService(db)
    return review_service.get_all_trainer_reviews()


@router.delete(
    "/admin/reviews/gyms/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_gym_review(
    review_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    review_service = ReviewService(db)
    review_service.delete_gym_review(review_id)
    return None


@router.delete(
    "/admin/reviews/trainers/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_trainer_review(
    review_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    review_service = ReviewService(db)
    review_service.delete_trainer_review(review_id)
    return None


@router.post(
    "/clients/me/reviews/gyms",
    response_model=GymReviewModel,
    status_code=status.HTTP_201_CREATED
)
async def create_gym_review(
    payload: GymReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    review_service = ReviewService(db)
    return review_service.create_gym_review(current_user, payload)


@router.post(
    "/clients/me/reviews/trainers",
    response_model=TrainerReviewModel,
    status_code=status.HTTP_201_CREATED
)
async def create_trainer_review(
    payload: TrainerReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    review_service = ReviewService(db)
    return review_service.create_trainer_review(current_user, payload)
