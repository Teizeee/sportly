import os
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException, status
import aiofiles
from PIL import Image
import io
import logging

from app.core.config import settings

class FileService:
    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def validate_file(self, file: UploadFile) -> None:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in settings.allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File extension {ext} not allowed. Allowed: {settings.allowed_extensions}"
            )
        
        if not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
    
    async def optimize_image(self, content: bytes, max_size: tuple = (800, 800)) -> bytes:
        try:
            img = Image.open(io.BytesIO(content))
            
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            if img.width > max_size[0] or img.height > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=85, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logging.error(f"Image optimization failed: {e}")
            return content
    
    async def save_file(self, file: UploadFile, filename: str = "") -> str:
        await self.validate_file(file)
        
        content = await file.read()
        
        if len(content) > settings.max_file_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File too large. Max size: {settings.max_file_size / 1024 / 1024} MB"
            )
        
        optimized_content = await self.optimize_image(content)
        
        ext = os.path.splitext(file.filename)[1].lower()
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            ext = '.jpg'
        
        filename = f"{filename}{ext}"
        file_path = self.storage_path / filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(optimized_content)
        
        return filename
    
    async def delete_file(self, filename: str) -> bool:
        file_path = self.storage_path / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    
    def get_file_url(self, filename: str, endpoint: str) -> str:
        return f"/{endpoint}/{filename}"