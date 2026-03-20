from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.subscription import PlatformSubscription


class PlatformSubscriptionRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, platform_sub_id: str) -> Optional[PlatformSubscription]:
        return self.db.query(PlatformSubscription).filter(PlatformSubscription.id == platform_sub_id).first()

    def get_all(self) -> List[PlatformSubscription]:
        return self.db.query(PlatformSubscription).all()