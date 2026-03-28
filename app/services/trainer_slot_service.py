from datetime import date, datetime, time, timedelta
from typing import List

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.booking import BookingStatus, TrainerSlot
from app.models.gym import GymSchedule
from app.models.trainer import Trainer
from app.models.user import User
from app.repositories.trainer_repository import TrainerRepository
from app.repositories.trainer_slot_repository import TrainerSlotRepository
from app.schemas.trainer_slot import TrainerSlotAvailability, TrainerSlotDayDeleteResult


class TrainerSlotService:
    def __init__(self, db: Session):
        self.db = db
        self.trainer_repo = TrainerRepository(db)
        self.trainer_slot_repo = TrainerSlotRepository(db)

    def get_day_slots(self, trainer_id: str, slot_date: date) -> List[TrainerSlotAvailability]:
        trainer = self._get_trainer_or_404(trainer_id)
        intervals = self._build_day_intervals(trainer, slot_date)
        if not intervals:
            return []

        day_start = datetime.combine(slot_date, time.min)
        day_end = day_start + timedelta(days=1)
        existing_slots = self.trainer_slot_repo.get_by_trainer_and_range(trainer_id, day_start, day_end)
        slot_map = {(slot.start_time, slot.end_time): slot for slot in existing_slots}

        result: List[TrainerSlotAvailability] = []
        for start_at, end_at in intervals:
            existing_slot = slot_map.get((start_at, end_at))
            if existing_slot:
                result.append(self._to_availability(existing_slot))
                continue

            result.append(TrainerSlotAvailability(
                trainer_id=trainer_id,
                start_time=start_at,
                end_time=end_at,
                created_at=None
            ))
        return result

    def create_slot(self, current_user: User, trainer_id: str, start_time: datetime, end_time: datetime) -> TrainerSlotAvailability:
        trainer = self._get_trainer_or_404(trainer_id)
        self._validate_manage_permissions(current_user, trainer)
        self._validate_hour_slot(start_time, end_time)
        self._validate_slot_in_schedule(trainer, start_time, end_time)

        existing_any = self.trainer_slot_repo.get_exact_slot_any_status(trainer_id, start_time, end_time)
        if existing_any and existing_any.deleted_at is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot already exists"
            )
        if existing_any and existing_any.deleted_at is not None:
            restored_slot = self.trainer_slot_repo.restore(existing_any)
            return self._to_availability(restored_slot)

        slot = self.trainer_slot_repo.create(trainer_id, start_time, end_time)
        return self._to_availability(slot)

    def delete_slot(self, current_user: User, trainer_id: str, slot_id: str):
        trainer = self._get_trainer_or_404(trainer_id)
        self._validate_manage_permissions(current_user, trainer)

        slot = self.trainer_slot_repo.get_by_id(slot_id)
        if not slot or slot.trainer_id != trainer_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found"
            )
        self._ensure_slot_not_booked(slot)
        self.trainer_slot_repo.soft_delete(slot)

    def create_day_slots(self, current_user: User, trainer_id: str, slot_date: date) -> List[TrainerSlotAvailability]:
        trainer = self._get_trainer_or_404(trainer_id)
        self._validate_manage_permissions(current_user, trainer)
        intervals = self._build_day_intervals(trainer, slot_date)
        if not intervals:
            return []

        for start_at, end_at in intervals:
            existing_any = self.trainer_slot_repo.get_exact_slot_any_status(trainer_id, start_at, end_at)
            if existing_any and existing_any.deleted_at is None:
                continue
            if existing_any and existing_any.deleted_at is not None:
                self.trainer_slot_repo.restore(existing_any)
                continue
            self.trainer_slot_repo.create(trainer_id, start_at, end_at)

        return self.get_day_slots(trainer_id, slot_date)

    def delete_day_slots(self, current_user: User, trainer_id: str, slot_date: date) -> TrainerSlotDayDeleteResult:
        trainer = self._get_trainer_or_404(trainer_id)
        self._validate_manage_permissions(current_user, trainer)

        day_start = datetime.combine(slot_date, time.min)
        day_end = day_start + timedelta(days=1)
        slots = self.trainer_slot_repo.get_by_trainer_and_range(trainer_id, day_start, day_end)

        deleted_count = 0
        for slot in slots:
            self._ensure_slot_not_booked(slot)
            self.trainer_slot_repo.soft_delete(slot)
            deleted_count += 1

        return TrainerSlotDayDeleteResult(deleted_count=deleted_count)

    def _get_trainer_or_404(self, trainer_id: str) -> Trainer:
        trainer = self.trainer_repo.get_by_id(trainer_id)
        if not trainer:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Trainer not found"
            )
        return trainer

    @staticmethod
    def _validate_manage_permissions(current_user: User, trainer: Trainer):
        if current_user.role == "TRAINER":
            if not current_user.trainer_profile or current_user.trainer_profile.id != trainer.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return

        if current_user.role == "GYM_ADMIN":
            if not current_user.gym or current_user.gym.id != trainer.gym_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not enough permissions"
                )
            return

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    @staticmethod
    def _validate_hour_slot(start_time: datetime, end_time: datetime):
        if start_time >= end_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be before end_time"
            )
        if start_time.minute != 0 or start_time.second != 0 or start_time.microsecond != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_time must be on the hour"
            )
        if end_time.minute != 0 or end_time.second != 0 or end_time.microsecond != 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="end_time must be on the hour"
            )
        if end_time - start_time != timedelta(hours=1):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot duration must be exactly 1 hour"
            )
        if start_time.date() != end_time.date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot must be within one day"
            )

    def _validate_slot_in_schedule(self, trainer: Trainer, start_time: datetime, end_time: datetime):
        schedule = self._get_day_schedule_or_404(trainer, start_time.date())
        if start_time.time() < schedule.open_time or end_time.time() > schedule.close_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Slot is out of gym schedule"
            )

    def _build_day_intervals(self, trainer: Trainer, slot_date: date) -> List[tuple[datetime, datetime]]:
        schedule = self._get_day_schedule_or_404(trainer, slot_date)
        current_start = datetime.combine(slot_date, schedule.open_time)
        day_end = datetime.combine(slot_date, schedule.close_time)

        intervals: List[tuple[datetime, datetime]] = []
        while current_start + timedelta(hours=1) <= day_end:
            intervals.append((current_start, current_start + timedelta(hours=1)))
            current_start += timedelta(hours=1)
        return intervals

    @staticmethod
    def _ensure_slot_not_booked(slot: TrainerSlot):
        if slot.booking and slot.booking.status != BookingStatus.CANCELLED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete booked slot"
            )

    @staticmethod
    def _to_availability(slot: TrainerSlot) -> TrainerSlotAvailability:
        return TrainerSlotAvailability(
            id=slot.id,
            trainer_id=slot.trainer_id,
            start_time=slot.start_time,
            end_time=slot.end_time,
            created_at=slot.created_at
        )

    @staticmethod
    def _get_day_schedule_or_404(trainer: Trainer, slot_date: date) -> GymSchedule:
        target_day = slot_date.weekday()
        for schedule in trainer.gym.schedule:
            if schedule.day_of_week == target_day and schedule.open_time and schedule.close_time:
                return schedule
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym schedule for this day is not configured"
        )
