from sqlalchemy import Column, String, DateTime, Enum, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class GymApplicationStatus(str, enum.Enum):
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ON_MODERATION = "ON_MODERATION"


class GymStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    BLOCKED = "BLOCKED"


class GymApplication(Base):
    __tablename__ = "gym_application"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    title = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    description = Column(String(255), nullable=True)
    phone = Column(String(255), nullable=False)
    status = Column(Enum(GymApplicationStatus), nullable=False)
    comment = Column(String(255), nullable=True)  # комментарий от суперадмина
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    gym_admin_id = Column(String(36), ForeignKey("user.id"), nullable=False)

    gym_admin = relationship("User", back_populates="gym_application", uselist=False)
    gym = relationship("Gym", back_populates="gym_application", uselist=False)

    def __repr__(self):
        return f"<GymApplication {self.title} ({self.status})>"


class Gym(Base):
    __tablename__ = "gym"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    gym_application_id = Column(String(36), ForeignKey("gym_application.id"), nullable=False, unique=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    status = Column(Enum(GymStatus), nullable=False)

    gym_application = relationship("GymApplication", back_populates="gym", uselist=False)
    trainers = relationship("Trainer", back_populates="gym")

    def __repr__(self):
        return f"<Gym {self.id} ({self.status})>"

    @property
    def is_active(self) -> bool:
        return self.status == GymStatus.ACTIVE

    @property
    def is_blocked(self) -> bool:
        return self.status == GymStatus.BLOCKED