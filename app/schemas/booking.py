from datetime import date, datetime, time
from typing import List, Literal, Optional

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


class BookingGymShort(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    title: str = Field(..., min_length=1, max_length=255)


class BookingTrainerShort(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)


class ClientBookingItem(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    status: BookingStatus
    date: date
    start_time: time
    end_time: time
    gym: BookingGymShort
    trainer: BookingTrainerShort


class ClientBookingsResponse(BaseModel):
    upcoming: List[ClientBookingItem]
    past: List[ClientBookingItem]
