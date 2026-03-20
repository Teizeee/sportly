from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.gym import Gym, GymApplication
from app.models.user import User
from app.repositories.gym_application_repository import GymApplicationRepository
from app.repositories.gym_repository import GymRepository
from app.schemas.gym import ApproveGymApplication, BaseGymApplication, RejectGymApplication
from app.services.subscription_service import SubscriptionService


class GymService:
    def __init__(self, db: Session):
        self.db = db
        self.subscription_service = SubscriptionService(db)
        self.gym_application_repo = GymApplicationRepository(db)
        self.gym_repo = GymRepository(db)

    def gym_application(self, user: User, application: BaseGymApplication) -> GymApplication:
        if user.gym_application is None:
            return self.gym_application_repo.create(user.id, application)
        return self.gym_application_repo.update(user.gym_application, application)

    def approve_application(self, approve_application_data: ApproveGymApplication) -> Gym:
        application = self.gym_application_repo.get_by_id(approve_application_data.gym_application_id)
        sub = self.subscription_service.get_platform_subscription(approve_application_data.platform_subscription_id)
        if application:
            if application.status == "APPROVED":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Gym application already approved"
                )
            self.gym_application_repo.approve(application)
            gym = self.gym_repo.create(application.id)
            self.subscription_service.gym_subscription(gym.id, sub.value)
            return gym
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym application not found"
        )

    def reject_application(self, application_id: str, reject_application_data: RejectGymApplication) -> GymApplication:
        application = self.gym_application_repo.get_by_id(application_id)
        if application:
            return self.gym_application_repo.reject(application, reject_application_data.comment)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Gym application not found"
        )