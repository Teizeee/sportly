import uuid
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.booking import TrainerSlot


class TrainerSlotRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, slot_id: str) -> Optional[TrainerSlot]:
        return self.db.query(TrainerSlot).filter(
            TrainerSlot.id == slot_id,
            TrainerSlot.deleted_at.is_(None)
        ).first()

    def get_exact_slot(self, trainer_id: str, start_time: datetime, end_time: datetime) -> Optional[TrainerSlot]:
        return self.db.query(TrainerSlot).filter(
            TrainerSlot.trainer_id == trainer_id,
            TrainerSlot.start_time == start_time,
            TrainerSlot.end_time == end_time,
            TrainerSlot.deleted_at.is_(None)
        ).first()

    def get_exact_slot_any_status(self, trainer_id: str, start_time: datetime, end_time: datetime) -> Optional[TrainerSlot]:
        return self.db.query(TrainerSlot).filter(
            TrainerSlot.trainer_id == trainer_id,
            TrainerSlot.start_time == start_time,
            TrainerSlot.end_time == end_time
        ).first()

    def get_by_trainer_and_range(self, trainer_id: str, range_start: datetime, range_end: datetime) -> List[TrainerSlot]:
        return self.db.query(TrainerSlot).filter(
            TrainerSlot.trainer_id == trainer_id,
            TrainerSlot.start_time >= range_start,
            TrainerSlot.start_time < range_end,
            TrainerSlot.deleted_at.is_(None)
        ).order_by(TrainerSlot.start_time.asc()).all()

    def create(self, trainer_id: str, start_time: datetime, end_time: datetime) -> TrainerSlot:
        slot = TrainerSlot(
            id=str(uuid.uuid4()),
            trainer_id=trainer_id,
            start_time=start_time,
            end_time=end_time
        )
        self.db.add(slot)
        self.db.commit()
        self.db.refresh(slot)
        return slot

    def soft_delete(self, slot: TrainerSlot):
        slot.deleted_at = datetime.utcnow()
        self.db.commit()

    def restore(self, slot: TrainerSlot) -> TrainerSlot:
        slot.deleted_at = None
        self.db.commit()
        self.db.refresh(slot)
        return slot
