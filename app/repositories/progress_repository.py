import uuid
from datetime import datetime
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.models.progress import ClientProgress


class ProgressRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(
        self,
        user_id: str,
        weight: Decimal,
        height: Decimal,
        bmi: Decimal,
        recorded_at: datetime
    ) -> ClientProgress:
        progress = ClientProgress(
            id=str(uuid.uuid4()),
            user_id=user_id,
            weight=weight,
            height=height,
            bmi=bmi,
            recorded_at=recorded_at
        )
        self.db.add(progress)
        self.db.commit()
        self.db.refresh(progress)
        return progress

    def get_by_user_id(self, user_id: str) -> List[ClientProgress]:
        return self.db.query(ClientProgress).filter(
            ClientProgress.user_id == user_id
        ).order_by(
            ClientProgress.recorded_at.desc()
        ).all()
