from typing import List, Optional

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.gym import Gym, GymApplication
from app.models.user import User
from app.repositories.gym_application_repository import GymApplicationRepository
from app.repositories.gym_repository import GymRepository
from app.schemas.gym import ApproveGymApplication, BaseGymApplication, RejectGymApplication, UpdateGym
from app.services.subscription_service import SubscriptionService


class GymService:
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
        self.gym_application_repo = GymApplicationRepository(db)
        self.gym_repo = GymRepository(db)

    def get_gym_applications(self) -> List[GymApplication]:
        return self.gym_application_repo.get_all()

    def gym_application(self, user: User, application: BaseGymApplication) -> GymApplication:
        if not user.gym_application:
            return self.gym_application_repo.create(user.id, application)
        return self.gym_application_repo.update(user.gym_application, application)

    def approve_application(self, approve_application_data: ApproveGymApplication) -> Gym:
        application = self.gym_application_repo.get_by_id(approve_application_data.gym_application_id)
        sub = self.subscription_service.get_platform_subscription(approve_application_data.platform_subscription_id)
        if application:
            if application.status == "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Заявка на зал уже одобрена"
                )
            self.gym_application_repo.approve(application)
            gym = self.gym_repo.create(application.id)
            self.subscription_service.gym_subscription(gym.id, sub.value)
            return gym
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка на зал не найдена"
        )

    def reject_application(self, application_id: str, reject_application_data: RejectGymApplication) -> GymApplication:
        application = self.gym_application_repo.get_by_id(application_id)
        if application:
            return self.gym_application_repo.reject(application, reject_application_data.comment)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Заявка на зал не найдена"
        )
    

    def get_gyms(
        self,
        name: Optional[str] = None,
        city: Optional[str] = None,
        min_rating: Optional[int] = None
    ) -> List[Gym]:
        normalized_name = name.strip() if name and name.strip() else None
        normalized_city = city.strip() if city and city.strip() else None
        gyms = self.gym_repo.get_gyms(normalized_name, normalized_city, min_rating)
        ratings = self.gym_repo.get_gyms_ratings([gym.id for gym in gyms])

        for gym in gyms:
            gym.rating = ratings.get(gym.id)

        return gyms
    

    def get_gyms_count(self) -> int:
        return self.gym_repo.get_gyms_count()

    def update_gym(self, current_user: User, gym_id: str, update_gym_data: UpdateGym) -> Gym:
        gym = self.gym_repo.get_by_id(gym_id)
        if not gym:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )
        self.gym_application_repo.update(gym.gym_application, update_gym_data)
        self.gym_repo.update_schedule(gym, update_gym_data.schedule)
        if current_user.role == "SUPER_ADMIN":
            self.subscription_service.gym_subscription_repo.update(gym.subscription, update_gym_data.subscription.end_date)
        return gym
    
    def block_gym(self, gym_id: str, comment: str) -> Gym:
        gym = self.gym_repo.get_by_id(gym_id)
        if not gym:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )
        return self.gym_repo.block(gym, comment)
    
    def unblock_gym(self, gym_id: str) -> Gym:
        gym = self.gym_repo.get_by_id(gym_id)
        if not gym:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Зал не найден"
            )
        return self.gym_repo.unblock(gym)
