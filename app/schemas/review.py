from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class GymReviewCreate(BaseModel):
    gym_id: str = Field(..., min_length=1, max_length=36)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)


class TrainerReviewCreate(BaseModel):
    trainer_id: str = Field(..., min_length=1, max_length=36)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)


class GymReviewModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    gym_id: str = Field(..., min_length=1, max_length=36)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)
    created_at: datetime
    author: "ReviewUserInfo"

    model_config = ConfigDict(from_attributes=True)


class TrainerReviewModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    trainer_id: str = Field(..., min_length=1, max_length=36)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)
    created_at: datetime
    author: "ReviewUserInfo"

    model_config = ConfigDict(from_attributes=True)


class ReviewUserInfo(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)


class ReviewGymInfo(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    title: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=255)


class GymReviewAdminModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)
    created_at: datetime
    gym: ReviewGymInfo
    author: ReviewUserInfo


class TrainerReviewAdminModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=255)
    created_at: datetime
    gym: ReviewGymInfo
    trainer: ReviewUserInfo
    author: ReviewUserInfo
