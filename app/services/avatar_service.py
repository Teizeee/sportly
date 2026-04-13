from sqlalchemy.orm import Session
from fastapi import File, HTTPException, status

from app.core.config import settings
from app.repositories.avatar_repository import AvatarRepository
from app.services.files import FileService


class AvatarService:
    def __init__(self, db: Session):
        self.db = db
        self.file_service = FileService(settings.avatar_path)
        self.avatar_repo = AvatarRepository(db)

    async def upload_avatar(self, user_id: str, file: File) -> str:
        filename = await self.file_service.save_file(file, user_id)
        avatar = self.avatar_repo.get_by_id(user_id)
        if avatar:
            return self.avatar_repo.update(avatar, f"/avatars/{filename}").link
        return self.avatar_repo.create(user_id, f"/avatars/{filename}").link

    def delete_avatar(self, user_id: str):
        avatar = self.avatar_repo.get_by_id(user_id)
        if avatar:
            self.avatar_repo.delete(avatar)
            return
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Аватар не найден"
        )