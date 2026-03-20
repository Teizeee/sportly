from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.gym import ApproveGymApplication, BaseGymApplication, RejectGymApplication
from app.services.gym_photo_service import GymPhotoService
from app.services.gym_service import GymService

router = APIRouter()

@router.post("/applications", status_code=status.HTTP_200_OK)
async def application(
    gym_application: BaseGymApplication,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_gym_admin)
):
    gym_service = GymService(db)
    return gym_service.gym_application(current_user, gym_application)

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


@router.post("/{gym_id}/photos", status_code=status.HTTP_201_CREATED)
async def upload_gym_photo(
    gym_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_admin)
):
    gym_photo_service = GymPhotoService(db)
    return await gym_photo_service.upload_photo(current_user, gym_id, file)


@router.delete("/{gym_id}/photos/{gym_photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_gym_photo(
    gym_id: str,
    gym_photo_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_admin)
):
    gym_photo_service = GymPhotoService(db)
    gym_photo_service.delete_photo(current_user, gym_id, gym_photo_id)
    return None