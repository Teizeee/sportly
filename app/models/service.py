from sqlalchemy import DECIMAL, Column, Date, Integer, SmallInteger, String, DateTime, Enum, ForeignKey, Time
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ClientMembershipStatus(enum.Enum):
    PURCHASED = "PURCHASED"
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"

class UserTrainerPackageStatus(enum.Enum):
    PURCHASED = "PURCHASED"
    ACTIVE = "ACTIVE"
    FINISHED = "FINISHED"


class MembershipType(Base):
    __tablename__ = "membership_type"

    id = Column(String(36), primary_key=True, unique=True, nullable=False)
    gym_id = Column(String(36), ForeignKey("gym.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    duration_months = Column(Integer, nullable=False)

    gym = relationship("Gym", back_populates="membership_types", uselist=False)

    def __repr__(self):
        return f"<MembershipType {self.name} - {self.price} руб.>"


class ClientMembership(Base):
    __tablename__ = "client_membership"

    id = Column(String(36), primary_key=True, unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    membership_type_id = Column(String(36), ForeignKey("membership_type.id"), nullable=False)
    status = Column(Enum(ClientMembershipStatus), nullable=False)
    purchased_at = Column(Date, nullable=False)
    activated_at = Column(Date, nullable=True)
    expires_at = Column(Date, nullable=True)

    user = relationship("User")
    membership_type = relationship("MembershipType")

    def __repr__(self):
        return f"<ClientMembership {self.id} - {self.status.value}>"


class TrainerPackage(Base):
    __tablename__ = "trainer_package"

    id = Column(String(36), primary_key=True, unique=True, nullable=False)
    trainer_id = Column(String(36), ForeignKey("trainer.id"), nullable=False)
    name = Column(String(255), nullable=False)
    session_count = Column(Integer, nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    description = Column(String(255), nullable=True)

    trainer = relationship("Trainer", back_populates="trainer_packages")

    def __repr__(self):
        return f"<TrainerPackage {self.name} - {self.session_count} занятий>"


class UserTrainerPackage(Base):
    __tablename__ = "user_trainer_package"

    id = Column(String(36), primary_key=True, unique=True, nullable=False)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    trainer_package_id = Column(String(36), ForeignKey("trainer_package.id"), nullable=False)
    status = Column(Enum(UserTrainerPackageStatus), nullable=False)
    sessions_left = Column(Integer, nullable=False)
    purchased_at = Column(Date, nullable=False)
    activated_at = Column(Date, nullable=True)
    expires_at = Column(Date, nullable=True)

    user = relationship("User")
    trainer_package = relationship("TrainerPackage")

    def __repr__(self):
        return f"<UserTrainerPackage {self.id} - {self.status.value}, занятий осталось: {self.sessions_left}>"