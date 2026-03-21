from typing import List, Optional
import uuid

from sqlalchemy.orm import Session

from app.models.gym import GymApplication, GymApplicationStatus
from app.schemas.gym import BaseGymApplication


class GymApplicationRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, gym_admin_id: str, application: BaseGymApplication) -> GymApplication:
        gym_application = GymApplication(
            id = uuid.uuid4(),
            title = application.title,
            address = application.address,
            description = application.description,
            phone = application.phone,
            status = GymApplicationStatus.ON_MODERATION,
            gym_admin_id = gym_admin_id
        )
        self.db.add(gym_application)
        self.db.commit()
        self.db.refresh(gym_application)
        return gym_application
    
    def get_all(self) -> List[GymApplication]:
        return self.db.query(GymApplication).filter(GymApplication.status == GymApplicationStatus.ON_MODERATION).all()

    def get_by_id(self, application_id: str) -> Optional[GymApplication]:
        return self.db.query(GymApplication).filter(GymApplication.id == application_id).first()

    def update(self, application: GymApplication, update_data: BaseGymApplication) -> GymApplication:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(application, field, value)
        if application.status != GymApplicationStatus.APPROVED:
            application.status = GymApplicationStatus.ON_MODERATION
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def approve(self, application: GymApplication) -> GymApplication:
        application.status = GymApplicationStatus.APPROVED
        self.db.commit()
        self.db.refresh(application)
        return application
    
    def reject(self, application: GymApplication, comment: str) -> GymApplication:
        application.comment = comment
        application.status = GymApplicationStatus.REJECTED
        self.db.commit()
        self.db.refresh(application)
        return application