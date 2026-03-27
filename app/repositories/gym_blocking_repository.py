import uuid
from typing import Optional

from sqlalchemy.orm import Session

from app.models.gym import GymBlocking
from app.models.service import ClientMembership, MembershipType
from app.models.trainer import Trainer


class GymBlockingRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_gym_and_user_id(self, gym_id: str, user_id: str) -> Optional[GymBlocking]:
        return self.db.query(GymBlocking).filter(
            GymBlocking.gym_id == gym_id,
            GymBlocking.user_id == user_id
        ).first()

    def create(self, gym_id: str, user_id: str, comment: Optional[str]) -> GymBlocking:
        blocking = GymBlocking(
            id=uuid.uuid4(),
            gym_id=gym_id,
            user_id=user_id,
            comment=comment
        )
        self.db.add(blocking)
        self.db.commit()
        self.db.refresh(blocking)
        return blocking

    def delete(self, blocking: GymBlocking) -> None:
        self.db.delete(blocking)
        self.db.commit()

    def is_trainer_of_gym(self, gym_id: str, user_id: str) -> bool:
        return self.db.query(Trainer.id).filter(
            Trainer.gym_id == gym_id,
            Trainer.user_id == user_id
        ).first() is not None

    def is_client_of_gym(self, gym_id: str, user_id: str) -> bool:
        return self.db.query(ClientMembership.id).join(
            MembershipType,
            ClientMembership.membership_type_id == MembershipType.id
        ).filter(
            ClientMembership.user_id == user_id,
            MembershipType.gym_id == gym_id
        ).first() is not None
