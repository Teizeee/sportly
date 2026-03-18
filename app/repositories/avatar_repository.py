from sqlalchemy.orm import Session
from typing import Optional

from app.models.user import Avatar


class AvatarRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, link: str) -> Avatar:
        avatar = Avatar(
            user_id = user_id,
            link = link
        )
        self.db.add(avatar)
        self.db.commit()
        self.db.refresh(avatar)
        return avatar

    def get_by_id(self, user_id: str) -> Optional[Avatar]:
        return self.db.query(Avatar).filter(Avatar.user_id == user_id).first()

    def update(self, avatar: Avatar, link: str) -> Avatar:
        avatar.link = link
        self.db.commit()
        self.db.refresh(avatar)
        return avatar

    def delete(self, avatar: Avatar) -> None:
        self.db.delete(avatar)
        self.db.commit()
