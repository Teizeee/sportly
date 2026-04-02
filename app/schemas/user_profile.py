from datetime import datetime
from typing import Optional

from pydantic import ConfigDict

from app.schemas.gym import GetGym, GetGymApplication
from app.schemas.user import AvatarResponse, GetUserTrainer


class UserResponse(GetUserTrainer):
    created_at: datetime
    blocked_comment: Optional[str] = None
    deleted_at: Optional[datetime] = None

    avatar: Optional[AvatarResponse] = None

    gym_application: Optional[GetGymApplication] = None
    gym: Optional[GetGym] = None

    model_config = ConfigDict(from_attributes=True)