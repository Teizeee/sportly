from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.models.booking import BookingStatus


class BookingBulkCreateItem(BaseModel):
    trainer_slot_id: str = Field(..., min_length=1, max_length=36)


class BookingAttendanceUpdate(BaseModel):
    status: Literal[BookingStatus.VISITED, BookingStatus.NOT_VISITED]


class BookingModel(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    trainer_slot_id: str = Field(..., min_length=1, max_length=36)
    user_trainer_package_id: str = Field(..., min_length=1, max_length=36)
    status: BookingStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
