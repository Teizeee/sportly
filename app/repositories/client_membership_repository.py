from datetime import date
import uuid
from typing import Dict, List, Optional

from sqlalchemy import case
from sqlalchemy.orm import Session, joinedload

from app.models.service import ClientMembership, ClientMembershipStatus, MembershipType


class ClientMembershipRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, user_id: str, membership_type_id: str) -> ClientMembership:
        client_membership = ClientMembership(
            id=str(uuid.uuid4()),
            user_id=user_id,
            membership_type_id=membership_type_id,
            status=ClientMembershipStatus.PURCHASED,
            purchased_at=date.today(),
            activated_at=None,
            expires_at=None
        )
        self.db.add(client_membership)
        self.db.commit()
        self.db.refresh(client_membership)
        return client_membership

    def get_by_id(self, membership_id: str) -> Optional[ClientMembership]:
        return self.db.query(ClientMembership).filter(
            ClientMembership.id == membership_id
        ).first()

    def get_by_user_id_ordered(self, user_id: str) -> List[ClientMembership]:
        status_order = case(
            (ClientMembership.status == ClientMembershipStatus.ACTIVE, 0),
            (ClientMembership.status == ClientMembershipStatus.PURCHASED, 1),
            else_=2
        )
        return self.db.query(ClientMembership).filter(
            ClientMembership.user_id == user_id
        ).order_by(
            status_order.asc(),
            ClientMembership.purchased_at.desc()
        ).all()

    def get_active_by_user_id(self, user_id: str) -> Optional[ClientMembership]:
        return self.db.query(ClientMembership).filter(
            ClientMembership.user_id == user_id,
            ClientMembership.status == ClientMembershipStatus.ACTIVE
        ).order_by(
            ClientMembership.activated_at.desc()
        ).first()

    def get_active_by_user_ids_for_gym(
        self,
        user_ids: List[str],
        gym_id: str
    ) -> Dict[str, ClientMembership]:
        if not user_ids:
            return {}

        active_memberships = self.db.query(ClientMembership).join(
            MembershipType, MembershipType.id == ClientMembership.membership_type_id
        ).options(
            joinedload(ClientMembership.membership_type)
        ).filter(
            ClientMembership.user_id.in_(user_ids),
            ClientMembership.status == ClientMembershipStatus.ACTIVE,
            MembershipType.gym_id == gym_id
        ).order_by(
            ClientMembership.user_id.asc(),
            ClientMembership.activated_at.desc()
        ).all()

        result: Dict[str, ClientMembership] = {}
        for membership in active_memberships:
            if membership.user_id not in result:
                result[membership.user_id] = membership
        return result

    def has_active_membership_for_gym(self, user_id: str, gym_id: str) -> bool:
        return self.db.query(ClientMembership).join(
            MembershipType, MembershipType.id == ClientMembership.membership_type_id
        ).filter(
            ClientMembership.user_id == user_id,
            ClientMembership.status == ClientMembershipStatus.ACTIVE,
            MembershipType.gym_id == gym_id
        ).first() is not None

    def activate(self, membership: ClientMembership, activated_at: date, expires_at: date) -> ClientMembership:
        membership.status = ClientMembershipStatus.ACTIVE
        membership.activated_at = activated_at
        membership.expires_at = expires_at
        self.db.commit()
        self.db.refresh(membership)
        return membership
