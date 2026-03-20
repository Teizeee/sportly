from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api import dependencies
from app.core.database import get_db
from app.models.user import User
from app.schemas.subscription import EditSubscriptionText
from app.services.avatar_service import AvatarService
from app.services.subscription_service import SubscriptionService

router = APIRouter()

@router.get("/", status_code=status.HTTP_200_OK)
async def get_platform_subscriptions(
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_admin)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.get_platform_subscriptions()


@router.get("/text", status_code=status.HTTP_200_OK)
async def get_subscription_text(
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_admin)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.get_platform_subscription_text()


@router.put("/text", status_code=status.HTTP_200_OK)
async def edit_subscription_text(
    subscription_text: EditSubscriptionText,
    db: Session = Depends(get_db),
    _: User = Depends(dependencies.require_super_admin)
):
    subscription_service = SubscriptionService(db)
    return subscription_service.edit_platform_subscription_text(subscription_text)