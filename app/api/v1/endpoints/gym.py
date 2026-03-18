from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.services.gym_photo_service import GymPhotoService

router = APIRouter()

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