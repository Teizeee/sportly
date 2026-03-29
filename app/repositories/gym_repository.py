from typing import Dict, List, Optional
import uuid

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.models.gym import Gym, GymApplication, GymSchedule, GymStatus
from app.models.review import GymReview
from app.schemas.gym import GymScheduleModel


class GymRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, gym_id: str) -> Optional[Gym]:
        return self.db.query(Gym).filter(Gym.id == gym_id).first()

    def get_gyms(
        self,
        name: Optional[str] = None,
        city: Optional[str] = None,
        min_rating: Optional[int] = None
    ) -> List[Gym]:
        query = self.db.query(Gym).join(GymApplication, Gym.gym_application_id == GymApplication.id)

        if name:
            query = query.filter(func.lower(GymApplication.title).like(f"%{name.lower()}%"))

        if city:
            query = query.filter(func.lower(GymApplication.address).like(f"г. {city.lower()}%"))

        if min_rating is not None:
            avg_rating = func.avg(GymReview.rating)
            query = (
                query
                .outerjoin(
                    GymReview,
                    and_(
                        GymReview.gym_id == Gym.id,
                        GymReview.deleted_at.is_(None)
                    )
                )
                .group_by(Gym.id)
                .having(func.coalesce(avg_rating, 0) > min_rating)
            )

        return query.all()

    def get_gyms_count(self) -> int:
        return self.db.query(Gym).count()

    def get_gyms_ratings(self, gym_ids: List[str]) -> Dict[str, float]:
        if not gym_ids:
            return {}

        rows = (
            self.db.query(
                GymReview.gym_id,
                func.avg(GymReview.rating).label("avg_rating")
            )
            .filter(
                GymReview.gym_id.in_(gym_ids),
                GymReview.deleted_at.is_(None)
            )
            .group_by(GymReview.gym_id)
            .all()
        )

        return {
            gym_id: float(avg_rating)
            for gym_id, avg_rating in rows
            if avg_rating is not None
        }

    def create(self, gym_application_id: str) -> Gym:
        gym = Gym(
            id=uuid.uuid4(),
            gym_application_id=gym_application_id,
            status=GymStatus.ACTIVE,
            schedule=[
                GymSchedule(id=uuid.uuid4(), day_of_week=0),
                GymSchedule(id=uuid.uuid4(), day_of_week=1),
                GymSchedule(id=uuid.uuid4(), day_of_week=2),
                GymSchedule(id=uuid.uuid4(), day_of_week=3),
                GymSchedule(id=uuid.uuid4(), day_of_week=4),
                GymSchedule(id=uuid.uuid4(), day_of_week=5),
                GymSchedule(id=uuid.uuid4(), day_of_week=6),
            ]
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

    def block(self, gym: Gym, comment: str) -> Gym:
        gym.status = GymStatus.BLOCKED
        gym.gym_application.comment = comment
        self.db.commit()
        self.db.refresh(gym)
        return gym

    def unblock(self, gym: Gym) -> Gym:
        gym.status = GymStatus.ACTIVE
        self.db.commit()
        self.db.refresh(gym)
        return gym
