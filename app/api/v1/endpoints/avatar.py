from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.services.avatar_service import AvatarService

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    avatar_service = AvatarService(db)
    return await avatar_service.upload_avatar(current_user.id, file)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def delete_avatar(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    avatar_service = AvatarService(db)
    avatar_service.delete_avatar(current_user.id)
    return None