from sqlalchemy.orm import Session
from fastapi import File, HTTPException, status

from app.core.config import settings
from app.models.user import User
from app.repositories.gym_photo_repository import GymPhotoRepository
from app.services.files import FileService


class GymPhotoService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService(settings.gym_path)
        self.gym_photo_repo = GymPhotoRepository(db)

    async def upload_photo(self, user: User, gym_id: str, file: File) -> str:
        if user.role == "SUPER_ADMIN" or user.gym.id == gym_id:
            filename = await self.file_service.save_file(file, gym_id)
            gym_photo = self.gym_photo_repo.get_by_id(gym_id)
            if gym_photo:
                return self.gym_photo_repo.update(gym_photo, f"/gyms/{filename}").link
            return self.gym_photo_repo.create(gym_id, f"/gyms/{filename}").link
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    def delete_photo(self, user: User, gym_id: str):
        if user.role == "SUPER_ADMIN" or user.gym.id == gym_id:
            gym_photo = self.gym_photo_repo.get_by_id(gym_id)
            if gym_photo:
                self.gym_photo_repo.delete(gym_photo)
                return
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Photo not found"
            )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
