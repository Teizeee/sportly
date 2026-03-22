from typing import List
import uuid

from sqlalchemy.orm import Session

from app.models.service import MembershipType
from app.schemas.service import MembershipTypeBase


class MembershipTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, membership_type_id: str) -> MembershipType:
        return self.db.query(MembershipType).filter(MembershipType.id == membership_type_id).first()

    def get_by_gym_id(self, gym_id: str) -> List[MembershipType]:
        return self.db.query(MembershipType).filter(MembershipType.gym_id == gym_id).all()
    
    def create(self, gym_id: str, membership_type_data: MembershipTypeBase) -> MembershipType:
        membership_type = MembershipType(
            id=str(uuid.uuid4()),
            gym_id=gym_id,
            name=membership_type_data.name,
            description=membership_type_data.description,
            price=membership_type_data.price,
            duration_months=membership_type_data.duration_months
        )
        self.db.commit()
        self.db.refresh(membership_type)
        return membership_type
    
    def update(self, membership_type: MembershipType, update_data: MembershipTypeBase) -> MembershipType:
        for field, value in update_data.model_dump(exclude_unset=True).items():
            setattr(membership_type, field, value)
        self.db.commit()
        self.db.refresh(membership_type)
        return membership_type

    def delete(self, membership_type: MembershipType):
        self.db.delete(membership_type)
        self.db.commit()