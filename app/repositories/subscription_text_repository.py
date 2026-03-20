from sqlalchemy.orm import Session

from app.models.subscription import SubscriptionText
from app.schemas.subscription import EditSubscriptionText


class SubscriptionTextRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self) -> SubscriptionText:
        return self.db.query(SubscriptionText).first()
    
    def update(self, subscription_text: SubscriptionText, subcription_text_data: EditSubscriptionText) -> SubscriptionText:
        subscription_text.description = subcription_text_data.description
        self.db.commit()
        self.db.refresh(subscription_text)
        return subscription_text
