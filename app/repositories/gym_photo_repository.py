import uuid

from sqlalchemy.orm import Session
from typing import Optional

from app.models.gym import GymPhoto


class GymPhotoRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, gym_id: str, link: str) -> GymPhoto:
        gym_photo = GymPhoto(
            id = uuid.uuid4(),
            gym_id = gym_id,
            link = link
        )
        self.db.add(gym_photo)
        self.db.commit()
        self.db.refresh(gym_photo)
        return gym_photo

    def get_by_id(self, id: str) -> Optional[GymPhoto]:
        return self.db.query(GymPhoto).filter(GymPhoto.id == id).first()

    def update(self, gym_photo: GymPhoto, link: str) -> GymPhoto:
        gym_photo.link = link
        self.db.commit()
        self.db.refresh(gym_photo)
        return gym_photo

    def delete(self, gym_photo: GymPhoto) -> None:
        self.db.delete(gym_photo)
        self.db.commit()
