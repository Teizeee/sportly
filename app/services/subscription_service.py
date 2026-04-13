from datetime import date
from typing import List

from dateutil.relativedelta import relativedelta
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.subscription import GymSubscription, PlatformSubscription, SubscriptionText
from app.repositories.gym_subscription_repository import GymSubscriptionRepository
from app.repositories.platform_subscription_repository import PlatformSubscriptionRepository
from app.repositories.subscription_text_repository import SubscriptionTextRepository
from app.schemas.subscription import EditSubscriptionText


class SubscriptionService:
    def __init__(self, db: Session):
        self.db = db
        self.platform_subscription_repo = PlatformSubscriptionRepository(db)
        self.gym_subscription_repo = GymSubscriptionRepository(db)
        self.subscription_text_repo = SubscriptionTextRepository(db)

    def get_platform_subscriptions(self) -> List[PlatformSubscription]:
        return self.platform_subscription_repo.get_all()

    def get_platform_subscription(self, platform_sub_id: str) -> PlatformSubscription:
        sub = self.platform_subscription_repo.get_by_id(platform_sub_id)
        if sub:
            return sub
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Подписка платформы не найдена"
        )

    def get_platform_subscription_text(self) -> SubscriptionText:
        return self.subscription_text_repo.get()
    
    def edit_platform_subscription_text(self, subscription_text: EditSubscriptionText) -> SubscriptionText:
        return self.subscription_text_repo.update(
            self.subscription_text_repo.get(),
            subscription_text
        )
    
    def gym_subscription(self, gym_id: str, month_count: int) -> GymSubscription:
        gym_sub = self.gym_subscription_repo.get_by_gym_id(gym_id)
        if gym_sub:
            return self.gym_subscription_repo.update(gym_sub, gym_sub.end_date + relativedelta(months=month_count))
        return self.gym_subscription_repo.create(gym_id, date.today() + relativedelta(months=month_count))