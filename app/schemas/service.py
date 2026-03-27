from decimal import Decimal
from datetime import date
from typing import Optional

from pydantic import BaseModel, Field

from app.models.service import ClientMembershipStatus, UserTrainerPackageStatus
from app.schemas.user import GetTrainer

class MembershipTypeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=255)
    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    duration_months: int = Field(..., ge=1)


class MembershipTypeModel(MembershipTypeBase):
    id: str = Field(..., min_length=1, max_length=36)


class TrainerPackageBase(BaseModel):
    trainer_id: str = Field(..., min_length=1, max_length=36)
    name: str = Field(..., min_length=1, max_length=255)
    session_count: int = Field(..., ge=1)
    price: Decimal = Field(..., max_digits=10, decimal_places=2)
    description: Optional[str] = Field(None, max_length=255)


class TrainerPackageModel(TrainerPackageBase):
    id: str = Field(..., min_length=1, max_length=36)
    trainer: GetTrainer = None


class ClientMembershipCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=36)
    membership_type_id: str = Field(..., min_length=1, max_length=36)


class ClientMembershipModel(ClientMembershipCreate):
    id: str = Field(..., min_length=1, max_length=36)
    status: ClientMembershipStatus
    purchased_at: date
    activated_at: Optional[date] = None
    expires_at: Optional[date] = None


class UserTrainerPackageCreate(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=36)
    trainer_package_id: str = Field(..., min_length=1, max_length=36)


class UserTrainerPackageModel(UserTrainerPackageCreate):
    id: str = Field(..., min_length=1, max_length=36)
    status: UserTrainerPackageStatus
    sessions_left: int = Field(..., ge=0)
    purchased_at: date
    activated_at: Optional[date] = None
    expires_at: Optional[date] = None
