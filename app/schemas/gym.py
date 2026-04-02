from __future__ import annotations

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.gym import GymApplicationStatus, GymStatus
from app.schemas.service import MembershipTypeModel, TrainerPackageModel


class BaseGymApplication(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=255)

class ApproveGymApplication(BaseModel):
    gym_application_id: str = Field(..., min_length=1, max_length=36)
    platform_subscription_id: str = Field(..., min_length=1, max_length=36)

class RejectGymApplication(BaseModel):
    comment: str = Field(..., min_length=1, max_length=255)

class BlockGym(BaseModel):
    comment: str = Field(..., min_length=1, max_length=255)


class GymPhotoModel(BaseModel):
    link: str = Field(..., min_length=1, max_length=255)


class GetGym(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    status: GymStatus = GymStatus.ACTIVE
    rating: Optional[float] = Field(default=None, ge=1, le=5)
    photo: Optional[GymPhotoModel] = None
    gym_application: GetGymApplication = None
    schedule: List[GymScheduleModel] = []
    subscription: Optional[Subscription] = None
    membership_types: List[MembershipTypeModel] = []
    trainer_packages: List[TrainerPackageModel] = []

class GetGymApplication(BaseGymApplication):
    id: str = Field(..., min_length=1, max_length=36)
    status: GymApplicationStatus = GymApplicationStatus.ON_MODERATION
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class GetGymApplicationAdmin(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    last_name: str = Field(..., min_length=1, max_length=255)
    first_name: str = Field(..., min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)
    email: str = Field(..., min_length=1, max_length=255)

    model_config = ConfigDict(from_attributes=True)


class GetGymApplicationWithAdmin(GetGymApplication):
    gym_admin: GetGymApplicationAdmin

    model_config = ConfigDict(from_attributes=True)

class GymScheduleModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    day_of_week: int = Field(..., nullable=False)
    open_time: Optional[time] = None
    close_time: Optional[time] = None

class UpdateGym(BaseGymApplication):
    schedule: List[GymScheduleModel]
    subscription: Optional[Subscription] = None

class Subscription(BaseModel):
    end_date: date
