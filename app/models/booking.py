import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    CREATED = "CREATED"
    CANCELLED = "CANCELLED"
    VISITED = "VISITED"
    NOT_VISITED = "NOT_VISITED"


class TrainerSlot(Base):
    __tablename__ = "trainer_slot"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    trainer_id = Column(String(36), ForeignKey("trainer.id"), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    trainer = relationship("Trainer", uselist=False)
    booking = relationship("Booking", back_populates="trainer_slot", uselist=False)

    def __repr__(self):
        return f"<TrainerSlot {self.id} trainer={self.trainer_id}>"


class Booking(Base):
    __tablename__ = "booking"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    trainer_slot_id = Column(String(36), ForeignKey("trainer_slot.id"), nullable=False, unique=True)
    user_trainer_package_id = Column(String(36), ForeignKey("user_trainer_package.id"), nullable=False)
    status = Column(Enum(BookingStatus), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())

    user = relationship("User", uselist=False)
    trainer_slot = relationship("TrainerSlot", back_populates="booking", uselist=False)
    user_trainer_package = relationship("UserTrainerPackage", uselist=False)

    def __repr__(self):
        return f"<Booking {self.id} status={self.status}>"
