from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.booking import BookingAttendanceUpdate, BookingBulkCreateItem, BookingModel, ClientBookingsResponse
from app.services.booking_service import BookingService

router = APIRouter()


@router.get(
    "/me/bookings",
    response_model=ClientBookingsResponse,
    status_code=status.HTTP_200_OK
)
async def get_my_bookings(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    booking_service = BookingService(db)
    return booking_service.get_my_bookings(current_user)


@router.post(
    "/me/bookings/bulk",
    response_model=List[BookingModel],
    status_code=status.HTTP_201_CREATED
)
async def create_my_bulk_bookings(
    payload: List[BookingBulkCreateItem],
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    booking_service = BookingService(db)
    return booking_service.create_my_bulk_bookings(current_user, payload)


@router.post(
    "/bookings/{booking_id}/cancel",
    response_model=BookingModel,
    status_code=status.HTTP_200_OK
)
async def cancel_booking(
    booking_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    booking_service = BookingService(db)
    return booking_service.cancel_booking(current_user, booking_id)


@router.post(
    "/bookings/{booking_id}/attendance",
    response_model=BookingModel,
    status_code=status.HTTP_200_OK
)
async def update_booking_attendance(
    booking_id: str,
    payload: BookingAttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    booking_service = BookingService(db)
    return booking_service.update_booking_attendance(current_user, booking_id, payload)
