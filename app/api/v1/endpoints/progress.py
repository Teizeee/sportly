from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.progress import ClientProgressCreate, ClientProgressModel
from app.services.progress_service import ProgressService

router = APIRouter()


@router.post(
    "/me/progress",
    response_model=ClientProgressModel,
    status_code=status.HTTP_201_CREATED
)
async def create_client_progress(
    progress_data: ClientProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    progress_service = ProgressService(db)
    return progress_service.create_progress(current_user, progress_data)


@router.get(
    "/me/progress",
    response_model=List[ClientProgressModel],
    status_code=status.HTTP_200_OK
)
async def get_my_client_progress(
    db: Session = Depends(get_db),
    current_user: User = Depends(dependencies.require_client)
):
    progress_service = ProgressService(db)
    return progress_service.get_my_progress(current_user)
