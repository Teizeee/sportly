from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from app.core.database import Base


class Trainer(Base):
    __tablename__ = "trainer"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    user_id = Column(String(36), ForeignKey("user.id"), nullable=False, unique=True)
    gym_id = Column(String(36), ForeignKey("gym.id"), nullable=False)
    phone = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # нехэшированный пароль для админа зала

    user = relationship("User", back_populates="trainer_profile", uselist=False)
    gym = relationship("Gym", back_populates="trainers", uselist=False)
    trainer_packages = relationship("TrainerPackage", back_populates="trainer")

    def __repr__(self):
        return f"<Trainer {self.id} for user {self.user_id}>"