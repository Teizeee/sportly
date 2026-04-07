from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.booking import BookingStatus


class TrainerSlotCreate(BaseModel):
    start_time: datetime
    end_time: datetime


class BookedUserShort(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)


class TrainerSlotAvailability(BaseModel):
    id: Optional[str] = Field(None, min_length=1, max_length=36)
    trainer_id: str = Field(..., min_length=1, max_length=36)
    start_time: datetime
    end_time: datetime
    created_at: Optional[datetime] = None
    booking_id: Optional[str] = Field(None, min_length=1, max_length=36)
    booking_status: Optional[BookingStatus] = None
    booked_user: Optional[BookedUserShort] = None


class TrainerSlotDayDeleteResult(BaseModel):
    deleted_count: int = 0
