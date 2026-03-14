from sqlalchemy import Column, String, DateTime, Enum, Date
from sqlalchemy.sql import func
import enum

from app.core.database import Base


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
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    blocked_at = Column(DateTime, nullable=True)
    blocked_comment = Column(String(255), nullable=True)
    deleted_at = Column(DateTime, nullable=True)

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
