from typing import Optional

from sqlalchemy import Column, ForeignKey, String, DateTime, Enum, Date
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base
from app.models.gym import Gym, GymApplicationStatus


class UserRole(str, enum.Enum):
    CLIENT = "CLIENT"
    TRAINER = "TRAINER"
    GYM_ADMIN = "GYM_ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(Base):
    __tablename__ = "user"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    role = Column(Enum(UserRole), nullable=False)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    patronymic = Column(String(255), nullable=True)
    email = Column(String(255), nullable=False, unique=True, index=True)
    password = Column(String(255), nullable=False)
    birth_date = Column(Date, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    blocked_at = Column(DateTime, nullable=True)
    blocked_comment = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

    trainer_profile = relationship("Trainer", back_populates="user", uselist=False)
    gym_application = relationship(
        "GymApplication", 
        back_populates="gym_admin", 
        uselist=False
    )
    avatar = relationship(
        "Avatar",
        uselist=False,
        cascade="all, delete-orphan"
    )
    gym_blockings = relationship("GymBlocking", back_populates="user", order_by="GymBlocking.created_at.desc()")

    def __repr__(self):
        return f"<User {self.email}>"

    @property
    def is_active(self) -> bool:
        return self.blocked_at is None and self.deleted_at is None

    @property
    def is_blocked(self) -> bool:
        return self.blocked_at is not None

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None

    @property
    def is_trainer(self) -> bool:
        return self.role == UserRole.TRAINER and self.trainer_profile is not None
    
    @property
    def gym(self) -> Optional[Gym]:
        if self.role != UserRole.GYM_ADMIN or not self.gym_application:
            return None
        
        if self.gym_application.status == GymApplicationStatus.APPROVED:
            return self.gym_application.gym
        return None
    

class Avatar(Base):
    __tablename__ = "avatar"

    user_id = Column(String(36), ForeignKey("user.id"), primary_key=True, index=True, unique=True)
    link = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Avatar for user {self.user_id}>"
