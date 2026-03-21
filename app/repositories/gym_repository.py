from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.gym import Gym, GymSchedule, GymStatus
from app.schemas.gym import GymScheduleModel


class GymRepository:
    def __init__(self, db: Session):
        self.db = db


    def get_by_id(self, gym_id: str) -> Optional[Gym]:
        return self.db.query(Gym).filter(Gym.id == gym_id).first()
    

    def get_gyms(self) -> List[Gym]:
        return self.db.query(Gym).all()
    

    def get_gyms_count(self) -> int:
        return self.db.query(Gym).count()


    def create(self, gym_application_id: str) -> Gym:
        gym = Gym(
            id = uuid.uuid4(),
            gym_application_id = gym_application_id,
            status = GymStatus.ACTIVE,
            schedule = [GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 0
            ), GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 1
            ), GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 2
            ), GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 3
            ), GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 4
            ), GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 5
            ), GymSchedule(
                id = uuid.uuid4(),
                day_of_week = 6
            )]
        )
        self.db.add(gym)
        self.db.commit()
        self.db.refresh(gym)
        return gym
    
    def update_schedule(self, gym: Gym, schedule: List[GymScheduleModel]) -> List[GymSchedule]:
        gym.schedule = [
            GymSchedule(
                id=uuid.uuid4(),
                gym_id=gym.id,
                day_of_week=item.day_of_week,
                open_time=item.open_time,
                close_time=item.close_time
            ) for item in schedule
        ]
        self.db.commit()
        self.db.refresh(gym)
        return gym.schedule
    
    def block(self, gym: Gym) -> Gym:
        gym.status = GymStatus.BLOCKED
        self.db.commit()
        self.db.refresh(gym)
        return gym
    
    def unblock(self, gym: Gym) -> Gym:
        gym.status = GymStatus.ACTIVE
        self.db.commit()
        self.db.refresh(gym)
        return gym