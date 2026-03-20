from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from app.models.user import User, UserRole
from app.models.trainer import Trainer
from app.schemas.user import UserCreate, UserUpdate, UserBlock


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email,
            password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            patronymic=user_data.patronymic,
            birth_date=user_data.birth_date,
            role=user_data.role,
            created_at=datetime.now(timezone.utc)
        )
        self.db.add(user)

        if user_data.role == "TRAINER":
            trainer = Trainer(
                id=str(uuid.uuid4()),
                user_id = user.id,
                gym_id = user_data.gym_id,
                phone = user_data.phone,
                description = user_data.description,
                password = user_data.password
            )
            self.db.add(trainer)

        self.db.commit()
        self.db.refresh(user)
        return user

    def get_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_all(
            self,
            skip: int = 0,
            limit: int = 100,
            include_deleted: bool = False,
            role: Optional[UserRole] = None
    ) -> List[User]:
        query = self.db.query(User)

        if not include_deleted:
            query = query.filter(User.deleted_at.is_(None))

        if role:
            query = query.filter(User.role == role)

        return query.offset(skip).limit(limit).all()

    def update(self, user: User, update_data: UserUpdate) -> User:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        self.db.commit()
        self.db.refresh(user)
        return user

    def block(self, user: User, block_data: UserBlock) -> User:
        user.blocked_at = datetime.now(timezone.utc)
        user.blocked_comment = block_data.comment
        self.db.commit()
        self.db.refresh(user)
        return user

    def unblock(self, user: User) -> User:
        user.blocked_at = None
        user.blocked_comment = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        user.deleted_at = datetime.now(timezone.utc)
        self.db.commit()

    def restore(self, user: User) -> User:
        user.deleted_at = None
        self.db.commit()
        self.db.refresh(user)
        return user

    def update_password(self, user: User, new_hashed_password: str) -> User:
        user.password = new_hashed_password
        self.db.commit()
        self.db.refresh(user)
        return user