from sqlalchemy import Column, DateTime, ForeignKey, SmallInteger, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class TrainerReview(Base):
    __tablename__ = "trainer_review"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    trainer_id = Column(String(36), ForeignKey("trainer.id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", uselist=False)
    trainer = relationship("Trainer", uselist=False)

    def __repr__(self):
        return f"<TrainerReview {self.id} rating={self.rating}>"


class GymReview(Base):
    __tablename__ = "gym_review"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False)
    gym_id = Column(String(36), ForeignKey("gym.id"), nullable=False)
    rating = Column(SmallInteger, nullable=False)
    comment = Column(String(255), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    deleted_at = Column(DateTime, nullable=True)

    user = relationship("User", uselist=False)
    gym = relationship("Gym", uselist=False)

    def __repr__(self):
        return f"<GymReview {self.id} rating={self.rating}>"
