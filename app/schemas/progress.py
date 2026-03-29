from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ClientProgressCreate(BaseModel):
    weight: Decimal = Field(..., gt=Decimal("0"), max_digits=5, decimal_places=2)
    height: Decimal = Field(..., gt=Decimal("0"), max_digits=5, decimal_places=2)
    bmi: Optional[Decimal] = Field(None, gt=Decimal("0"), max_digits=5, decimal_places=2)
    recorded_at: Optional[datetime] = None


class ClientProgressModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    weight: Decimal = Field(..., max_digits=5, decimal_places=2)
    height: Decimal = Field(..., max_digits=5, decimal_places=2)
    bmi: Decimal = Field(..., max_digits=5, decimal_places=2)
    recorded_at: datetime

    model_config = ConfigDict(from_attributes=True)
