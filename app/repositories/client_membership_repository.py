from datetime import date
import uuid

from sqlalchemy.orm import Session

from app.models.service import ClientMembership, ClientMembershipStatus


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
