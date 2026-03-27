from sqlalchemy import case, exists, func
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import Optional, List
import uuid

from app.models.gym import Gym, GymApplication, GymBlocking
from app.models.service import ClientMembership, MembershipType
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
            gym_id: Optional[str] = None,
            role: Optional[UserRole] = None,
            is_blocked: Optional[bool] = None
    ) -> List[User]:
        query = self.db.query(User).filter(User.deleted_at.is_(None))

        if role:
            query = query.filter(User.role == role)

        if role == "SUPER_ADMIN":
            return query.all()

        if gym_id:
            match role:
                case "CLIENT":
                    query = query.filter(
                        exists().where(
                            (ClientMembership.user_id == User.id) &
                            (ClientMembership.membership_type_id == MembershipType.id) &
                            (MembershipType.gym_id == gym_id)
                        )
                    )
                case "TRAINER":
                    query = query.filter(
                        User.trainer_profile.has(
                            Trainer.gym_id == gym_id
                        )
                    )
                case "GYM_ADMIN":
                    query = query.filter(
                        exists().where(
                            (GymApplication.gym_admin_id == User.id) &
                            (GymApplication.id == Gym.gym_application_id) &
                            (Gym.id == gym_id)
                        )
                    )

        if is_blocked is not None:
            if gym_id:
                gym_blocking_exists = exists().where(
                    (GymBlocking.user_id == User.id) &
                    (GymBlocking.gym_id == gym_id)
                )
                query = query.filter(gym_blocking_exists if is_blocked else ~gym_blocking_exists)
            else:
                query = query.filter(User.blocked_at.is_not(None) if is_blocked else User.blocked_at.is_(None))

        return query.all()
    
    def get_count(self):
        return self.db.query(
            func.count(User.id).label('total'),
            func.sum(case((User.role == 'CLIENT', 1), else_=0)).label('clients'),
            func.sum(case((User.role == 'TRAINER', 1), else_=0)).label('trainers'),
            func.sum(case((User.role == 'GYM_ADMIN', 1), else_=0)).label('gym_admins')
        ).filter(
            User.deleted_at.is_(None)
        ).first()

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
