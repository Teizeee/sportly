from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.service import (
    ActiveClientServicesModel,
    ClientMembershipModel,
    UserTrainerPackageModel
)
from app.services.client_service import ClientService

router = APIRouter()


@router.get(
    "/me/memberships",
    response_model=List[ClientMembershipModel],
    status_code=status.HTTP_200_OK
)
async def get_my_memberships(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    client_service = ClientService(db)
    return client_service.get_my_memberships(current_user)


@router.get(
    "/me/packages",
    response_model=List[UserTrainerPackageModel],
    status_code=status.HTTP_200_OK
)
async def get_my_packages(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    client_service = ClientService(db)
    return client_service.get_my_trainer_packages(current_user)


@router.get(
    "/me/active-services",
    response_model=ActiveClientServicesModel,
    status_code=status.HTTP_200_OK
)
async def get_my_active_services(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    client_service = ClientService(db)
    return client_service.get_my_active_services(current_user)


@router.post(
    "/me/memberships/{membership_id}/activate",
    response_model=ClientMembershipModel,
    status_code=status.HTTP_200_OK
)
async def activate_my_membership(
    membership_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    client_service = ClientService(db)
    return client_service.activate_my_membership(current_user, membership_id)


@router.post(
    "/me/packages/{user_trainer_package_id}/activate",
    response_model=UserTrainerPackageModel,
    status_code=status.HTTP_200_OK
)
async def activate_my_package(
    user_trainer_package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    client_service = ClientService(db)
    return client_service.activate_my_trainer_package(current_user, user_trainer_package_id)
