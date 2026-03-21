from sqlalchemy import Column, Date, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class SubscriptionText(Base):
    __tablename__ = "subscription_text"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    description = Column(Text, nullable=False)

    def __repr__(self):
        return f"<SubscriptionText {self.id}>"
    
class PlatformSubscription(Base):
    __tablename__ = "platform_subscriptions"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    value = Column(Integer, nullable=False, unique=True)  # Количество месяцев
    description = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<PlatformSubscription {self.id} - {self.value} ({self.description})>"
    
class GymSubscription(Base):
    __tablename__ = "gym_subscription"

    id = Column(String(36), primary_key=True, index=True, unique=True)
    gym_id = Column(String(36), ForeignKey("gym.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    gym = relationship("Gym", back_populates="subscription", uselist=False)

    def __repr__(self):
        return f"<GymSubscription {self.id} for gym {self.gym_id} ({self.start_date} - {self.end_date})>"

    @property
    def is_active(self) -> bool:
        """Проверяет, активна ли подписка на текущую дату."""
        from datetime import date
        today = date.today()
        return self.start_date <= today <= self.end_date

    @property
    def days_remaining(self) -> int:
        """Возвращает количество оставшихся дней подписки."""
        from datetime import date
        today = date.today()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days