from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.gym import (
    ApproveGymApplication,
    BaseGymApplication,
    BlockGym,
    GetGym,
    GetGymApplicationWithAdmin,
    RejectGymApplication,
    UpdateGym,
)
from app.schemas.user import GetTrainer
from app.services.gym_blocking_service import GymBlockingService
from app.services.gym_photo_service import GymPhotoService
from app.services.gym_service import GymService
from app.services.services_service import ServicesService

router = APIRouter()

@router.get(
    "/applications",
    status_code=status.HTTP_200_OK,
    response_model=List[GetGymApplicationWithAdmin],
    response_model_exclude_none=True
)
async def applications(
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    gym_service = GymService(db)
    return gym_service.get_gym_applications()

@router.post("/applications", status_code=status.HTTP_200_OK)
async def application(
    gym_application: BaseGymApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    gym_service = GymService(db)
    return gym_service.gym_application(current_user, gym_application)

@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    response_model=List[GetGym],
    response_model_exclude_none=True
)
async def get_gyms(
    name: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    rating: Optional[int] = Query(default=None, ge=1, le=5),
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    gym_service = GymService(db)
    gyms = gym_service.get_gyms(name=name, city=city, min_rating=rating)

    is_super_admin = current_user.role == "SUPER_ADMIN"

    if not is_super_admin:
        today = date.today()
        gyms = [
            gym for gym in gyms
            if gym.is_active
            and gym.subscription
            and gym.subscription.start_date <= today <= gym.subscription.end_date
        ]
        for gym in gyms:
            gym.subscription = None

    return gyms

@router.get(
    "/{gym_id}/trainers",
    response_model=List[GetTrainer],
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK
)
async def get_trainers(
        gym_id: str,
        db: Session = Depends(get_db),
        _: User = Depends(dependencies.get_current_active_user),
):
    services_service = ServicesService(db)
    return services_service.get_trainers(gym_id)

@router.get("/count", status_code=status.HTTP_200_OK)
async def get_gyms_count(
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    gym_service = GymService(db)
    return gym_service.get_gyms_count()

@router.post("/", status_code=status.HTTP_200_OK)
async def approve_application(
    approve_gym_application: ApproveGymApplication,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    gym_service = GymService(db)
    return gym_service.approve_application(approve_gym_application)

@router.patch("/applications/{application_id}/reject", status_code=status.HTTP_200_OK)
async def reject_application(
    application_id: str,
    reject_gym_application: RejectGymApplication,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    gym_service = GymService(db)
    return gym_service.reject_application(application_id, reject_gym_application)


@router.put("/{gym_id}", response_model=GetGym, status_code=status.HTTP_200_OK)
async def update_gym(
    gym_id: str,
    update_gym_data: UpdateGym,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_admin)
):
    gym_service = GymService(db)
    return gym_service.update_gym(current_user, gym_id, update_gym_data)


@router.post("/{gym_id}/block", response_model=GetGym, status_code=status.HTTP_200_OK)
async def block_gym(
    gym_id: str,
    block_gym_data: BlockGym,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    gym_service = GymService(db)
    return gym_service.block_gym(gym_id, block_gym_data.comment)


@router.post("/{gym_id}/unblock", response_model=GetGym, status_code=status.HTTP_200_OK)
async def unblock_gym(
    gym_id: str,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    gym_service = GymService(db)
    return gym_service.unblock_gym(gym_id)

@router.post("/{gym_id}/block/{user_id}", status_code=status.HTTP_200_OK)
async def block_user_in_gym(
    gym_id: str,
    user_id: str,
    comment: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    gym_blocking_service = GymBlockingService(db)
    return gym_blocking_service.block_user(current_user, gym_id, user_id, comment)


@router.post("/{gym_id}/unblock/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unblock_user_in_gym(
    gym_id: str,
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    gym_blocking_service = GymBlockingService(db)
    gym_blocking_service.unblock_user(current_user, gym_id, user_id)
    return None


@router.post("/{gym_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_gym_photo(
    gym_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_admin)
):
    gym_photo_service = GymPhotoService(db)
    return await gym_photo_service.upload_photo(current_user, gym_id, file)


@router.delete("/{gym_id}/photos", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gym_photo(
    gym_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_admin)
):
    gym_photo_service = GymPhotoService(db)
    gym_photo_service.delete_photo(current_user, gym_id)
    return None
