from datetime import date
from typing import Optional
import uuid

from sqlalchemy.orm import Session

from app.models.subscription import GymSubscription



class GymSubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_gym_id(self, gym_id: str) -> Optional[GymSubscription]:
        return self.db.query(GymSubscription).filter(GymSubscription.gym_id == gym_id).first()
    
    def create(self, gym_id: str, end_date: date) -> GymSubscription:
        gym_subscription = GymSubscription(
            id = uuid.uuid4(),
            gym_id = gym_id,
            start_date = date.today(),
            end_date = end_date
        )
        self.db.add(gym_subscription)
        self.db.commit()
        self.db.refresh(gym_subscription)
        return gym_subscription
    
    def update(self, gym_subscription: GymSubscription, end_date: date) -> GymSubscription:
        gym_subscription.end_date = end_date
        self.db.commit()
        self.db.refresh(gym_subscription)
        return gym_subscription