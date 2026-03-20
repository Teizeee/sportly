import uuid

from sqlalchemy.orm import Session

from app.models.gym import Gym, GymStatus


class GymRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, gym_application_id: str) -> Gym:
        gym = Gym(
            id = uuid.uuid4(),
            gym_application_id = gym_application_id,
            status = GymStatus.ACTIVE
        )
        self.db.add(gym)
        self.db.commit()
        self.db.refresh(gym)
        return gym