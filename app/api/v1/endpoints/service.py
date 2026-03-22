from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.service import MembershipTypeBase, TrainerPackageBase
from app.services.services_service import ServicesService

router = APIRouter()

@router.get("/{gym_id}/memberships", status_code=status.HTTP_200_OK)
async def get_memberships(
    gym_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.get_current_active_user),
):
    services_service = ServicesService(db)
    return services_service.get_membership_types(gym_id)

@router.post("/memberships", status_code=status.HTTP_201_CREATED)
async def create_membership(
    membership_data: MembershipTypeBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    services_service = ServicesService(db)
    return services_service.create_membership_type(current_user, membership_data)

@router.put("/memberships/{membership_type_id}", status_code=status.HTTP_200_OK)
async def update_membership(
    membership_type_id: str,
    membership_data: MembershipTypeBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    services_service = ServicesService(db)
    return services_service.update_membership_type(current_user, membership_type_id, membership_data)

@router.delete("/memberships/{membership_type_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_membership(
    membership_type_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    services_service = ServicesService(db)
    services_service.delete_membership_type(current_user, membership_type_id)
    return None

@router.get("/{gym_id}/packages", status_code=status.HTTP_200_OK)
async def get_trainer_packages(
    gym_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.get_current_active_user),
):
    services_service = ServicesService(db)
    return services_service.get_trainer_packages(gym_id)

@router.post("/packages", status_code=status.HTTP_201_CREATED)
async def create_trainer_package(
    trainer_package: TrainerPackageBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    services_service = ServicesService(db)
    return services_service.create_trainer_package(current_user, trainer_package)

@router.put("/packages/{trainer_package_id}", status_code=status.HTTP_200_OK)
async def update_trainer_package(
    trainer_package_id: str,
    trainer_package: TrainerPackageBase,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    services_service = ServicesService(db)
    return services_service.update_trainer_package(current_user, trainer_package_id, trainer_package)

@router.delete("/packages/{trainer_package_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trainer_package(
    trainer_package_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    services_service = ServicesService(db)
    services_service.delete_trainer_package(current_user, trainer_package_id)
    return None