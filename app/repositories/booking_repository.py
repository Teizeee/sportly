import uuid
from datetime import datetime
from typing import List

from sqlalchemy import and_
from sqlalchemy.orm import Session, joinedload

from app.models.booking import Booking, BookingStatus, TrainerSlot
from app.models.service import UserTrainerPackage


class BookingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_trainer_slot_ids(self, trainer_slot_ids: List[str]) -> List[Booking]:
        if not trainer_slot_ids:
            return []
        return self.db.query(Booking).filter(
            Booking.trainer_slot_id.in_(trainer_slot_ids)
        ).all()

    def get_by_id(self, booking_id: str) -> Booking | None:
        return self.db.query(Booking).options(
            joinedload(Booking.trainer_slot).joinedload(TrainerSlot.trainer),
            joinedload(Booking.user_trainer_package).joinedload(UserTrainerPackage.trainer_package)
        ).filter(
            Booking.id == booking_id
        ).first()

    def create_many(self, user_id: str, user_trainer_package_id: str, trainer_slot_ids: List[str]) -> List[Booking]:
        bookings: List[Booking] = []
        for slot_id in trainer_slot_ids:
            booking = Booking(
                id=str(uuid.uuid4()),
                user_id=user_id,
                trainer_slot_id=slot_id,
                user_trainer_package_id=user_trainer_package_id,
                status=BookingStatus.CREATED
            )
            self.db.add(booking)
            bookings.append(booking)
        return bookings

    def mark_past_created_as_not_visited(self, now: datetime | None = None) -> int:
        current_time = now or datetime.utcnow()
        updated = self.db.query(Booking).filter(
            and_(
                Booking.status == BookingStatus.CREATED,
                Booking.trainer_slot.has(TrainerSlot.start_time < current_time)
            )
        ).update(
            {Booking.status: BookingStatus.NOT_VISITED},
            synchronize_session=False
        )
        if updated:
            self.db.commit()
        return updated

    def has_visited_trainer(self, user_id: str, trainer_id: str) -> bool:
        return self.db.query(Booking).join(
            TrainerSlot, TrainerSlot.id == Booking.trainer_slot_id
        ).filter(
            Booking.user_id == user_id,
            Booking.status == BookingStatus.VISITED,
            TrainerSlot.trainer_id == trainer_id
        ).first() is not None
