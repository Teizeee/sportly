from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.service import ClientMembershipCreate, UserTrainerPackageCreate
from app.services.client_service import ClientService

router = APIRouter()


@router.post("/client-memberships", status_code=status.HTTP_201_CREATED)
async def create_client_membership(
    membership_data: ClientMembershipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    client_service = ClientService(db)
    return client_service.create_client_membership(current_user, membership_data)


@router.post("/user-trainer-packages", status_code=status.HTTP_201_CREATED)
async def create_user_trainer_package(
    package_data: UserTrainerPackageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    client_service = ClientService(db)
    return client_service.create_user_trainer_package(current_user, package_data)
