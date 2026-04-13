from datetime import date, datetime, timedelta, timezone
from typing import List

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.booking import Booking, BookingStatus
from app.models.service import UserTrainerPackageStatus
from app.models.user import User, UserRole
from app.repositories.booking_repository import BookingRepository
from app.repositories.trainer_slot_repository import TrainerSlotRepository
from app.repositories.user_trainer_package_repository import UserTrainerPackageRepository
from app.schemas.booking import (
    BookingAttendanceUpdate,
    BookingBulkCreateItem,
    BookingGymShort,
    BookingTrainerShort,
    ClientBookingItem,
    ClientBookingsResponse
)


class BookingService:
    def __init__(self, db: Session):
        self.db = db
        self.booking_repo = BookingRepository(db)
        self.trainer_slot_repo = TrainerSlotRepository(db)
        self.user_trainer_package_repo = UserTrainerPackageRepository(db)

    @staticmethod
    def _as_aware_utc(value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    def get_my_bookings(self, current_user: User) -> ClientBookingsResponse:
        bookings = self.booking_repo.get_client_bookings(current_user.id)
        now = datetime.now(timezone.utc)

        upcoming: List[ClientBookingItem] = []
        past: List[ClientBookingItem] = []

        for booking in bookings:
            slot = booking.trainer_slot
            trainer = slot.trainer
            trainer_user = trainer.user
            gym = trainer.gym
            gym_application = gym.gym_application

            item = ClientBookingItem(
                id=booking.id,
                status=booking.status,
                date=slot.start_time.date(),
                start_time=slot.start_time.time(),
                end_time=slot.end_time.time(),
                gym=BookingGymShort(
                    id=gym.id,
                    title=gym_application.title
                ),
                trainer=BookingTrainerShort(
                    id=trainer.id,
                    first_name=trainer_user.first_name,
                    last_name=trainer_user.last_name,
                    patronymic=trainer_user.patronymic
                )
            )

            is_past_by_status = booking.status in {BookingStatus.VISITED, BookingStatus.NOT_VISITED}
            slot_start_time = self._as_aware_utc(slot.start_time)
            is_past_by_time = slot_start_time < now

            if is_past_by_status or is_past_by_time:
                past.append(item)
            else:
                upcoming.append(item)

        return ClientBookingsResponse(
            upcoming=upcoming,
            past=past
        )

    def create_my_bulk_bookings(self, current_user: User, payload: List[BookingBulkCreateItem]) -> List[Booking]:
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one booking item is required"
            )

        self.user_trainer_package_repo.finish_expired_active_packages_for_user(current_user.id)
        active_package = self.user_trainer_package_repo.get_active_by_user_id_for_update(current_user.id)

        if not active_package:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active trainer package not found"
            )

        if active_package.activated_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Active trainer package is not activated"
            )

        slot_ids = [item.trainer_slot_id for item in payload]
        if len(set(slot_ids)) != len(slot_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate trainer_slot_id in request"
            )

        if active_package.sessions_left < len(slot_ids):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Not enough sessions_left in active trainer package"
            )

        slots = self.trainer_slot_repo.get_by_ids(slot_ids)
        slot_map = {slot.id: slot for slot in slots}
        missing_slot_ids = [slot_id for slot_id in slot_ids if slot_id not in slot_map]
        if missing_slot_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Slots not found: {', '.join(missing_slot_ids)}"
            )

        existing_bookings = self.booking_repo.get_by_trainer_slot_ids(slot_ids)
        active_existing_bookings = [
            booking for booking in existing_bookings if booking.status != BookingStatus.CANCELLED
        ]
        if active_existing_bookings:
            booked_slot_ids = ", ".join(sorted({booking.trainer_slot_id for booking in active_existing_bookings}))
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Slots already booked: {booked_slot_ids}"
            )
        cancelled_booking_by_slot_id = {
            booking.trainer_slot_id: booking
            for booking in existing_bookings
            if booking.status == BookingStatus.CANCELLED
        }

        package_trainer_id = active_package.trainer_package.trainer_id
        activated_at = active_package.activated_at
        expires_at = activated_at + relativedelta(months=1)
        today = date.today()

        for slot_id in slot_ids:
            slot = slot_map[slot_id]
            slot_date = slot.start_time.date()

            if slot.trainer_id != package_trainer_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Slot {slot.id} belongs to another trainer"
                )
            if slot_date < today:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Slot {slot.id} is in the past"
                )
            if slot_date < activated_at or slot_date > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Slot {slot.id} is out of package active period"
                )

        slot_ids_to_create = [slot_id for slot_id in slot_ids if slot_id not in cancelled_booking_by_slot_id]
        bookings = self.booking_repo.create_many(
            user_id=current_user.id,
            user_trainer_package_id=active_package.id,
            trainer_slot_ids=slot_ids_to_create
        )
        for slot_id in slot_ids:
            cancelled_booking = cancelled_booking_by_slot_id.get(slot_id)
            if not cancelled_booking:
                continue
            cancelled_booking.user_id = current_user.id
            cancelled_booking.user_trainer_package_id = active_package.id
            cancelled_booking.status = BookingStatus.CREATED
            bookings.append(cancelled_booking)
        active_package.sessions_left -= len(slot_ids)
        if active_package.sessions_left == 0:
            active_package.status = UserTrainerPackageStatus.FINISHED

        try:
            self.db.commit()
        except IntegrityError:
            self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Failed to create bookings due to concurrent update. Try again."
            )

        for booking in bookings:
            self.db.refresh(booking)
        return bookings

    def cancel_booking(self, current_user: User, booking_id: str) -> Booking:
        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )

        if booking.status != BookingStatus.CREATED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CREATED bookings can be cancelled"
            )

        if current_user.role == UserRole.CLIENT:
            if booking.user_id != current_user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            slot_start_time = self._as_aware_utc(booking.trainer_slot.start_time)
            if slot_start_time - datetime.now(timezone.utc) < timedelta(hours=3):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Booking can be cancelled at least 3 hours before training"
                )
        elif current_user.role == UserRole.GYM_ADMIN:
            if not current_user.gym:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Gym admin has no approved gym"
                )
            if booking.trainer_slot.trainer.gym_id != current_user.gym.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
        else:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )

        user_package = self.user_trainer_package_repo.get_by_id_for_update(booking.user_trainer_package_id)
        if not user_package:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User trainer package not found"
            )

        booking.status = BookingStatus.CANCELLED
        user_package.sessions_left += 1
        if (
            user_package.status == UserTrainerPackageStatus.FINISHED
            and user_package.activated_at
            and user_package.activated_at + relativedelta(months=1) > date.today()
        ):
            user_package.status = UserTrainerPackageStatus.ACTIVE

        self.db.commit()
        self.db.refresh(booking)
        return booking

    def update_booking_attendance(
        self,
        current_user: User,
        booking_id: str,
        payload: BookingAttendanceUpdate
    ) -> Booking:
        if current_user.role != UserRole.GYM_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        if not current_user.gym:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Gym admin has no approved gym"
            )

        booking = self.booking_repo.get_by_id(booking_id)
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        if booking.trainer_slot.trainer.gym_id != current_user.gym.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions"
            )
        can_update = (
            booking.status == BookingStatus.CREATED
            or (booking.status == BookingStatus.NOT_VISITED and payload.status == BookingStatus.VISITED)
        )
        if not can_update:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only CREATED bookings can be marked, or NOT_VISITED can be changed to VISITED"
            )

        booking.status = payload.status
        self.db.commit()
        self.db.refresh(booking)
        return booking
