from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

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