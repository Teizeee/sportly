from pydantic import BaseModel, ConfigDict, EmailStr, Field
from datetime import date, datetime
from typing import Optional
from app.models.user import UserRole
from app.models.service import ClientMembershipStatus, UserTrainerPackageStatus


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    role: UserRole = UserRole.CLIENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    phone: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=255)
    gym_id: Optional[str] = Field(None, min_length=1, max_length=36)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class AvatarResponse(BaseModel):
    link: str

class TrainerBase(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    gym_id: str = Field(..., min_length=1, max_length=36)
    phone: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=255)
    model_config = ConfigDict(from_attributes=True)


class GetUserWithId(UserBase):
    id: str = Field(..., min_length=1, max_length=36)
    model_config = ConfigDict(from_attributes=True)

class GetUserTrainer(GetUserWithId):
    trainer_profile: Optional[TrainerBase] = None
    blocked_at: Optional[datetime] = None


class TrainerBaseWithPassword(TrainerBase):
    password: Optional[str] = Field(None, min_length=1, max_length=255)


class ActiveClientMembership(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    membership_type_id: str = Field(..., min_length=1, max_length=36)
    membership_type_name: str = Field(..., min_length=1, max_length=255)
    status: ClientMembershipStatus
    purchased_at: date
    activated_at: Optional[date] = None
    expires_at: Optional[date] = None


class ActiveUserTrainerPackage(BaseModel):
    id: str = Field(..., min_length=1, max_length=36)
    user_id: str = Field(..., min_length=1, max_length=36)
    trainer_package_id: str = Field(..., min_length=1, max_length=36)
    trainer_package_name: str = Field(..., min_length=1, max_length=255)
    trainer_package_session_count: int = Field(..., ge=1)
    trainer_first_name: str = Field(..., min_length=1, max_length=255)
    trainer_last_name: str = Field(..., min_length=1, max_length=255)
    trainer_patronymic: Optional[str] = Field(None, max_length=255)
    status: UserTrainerPackageStatus
    sessions_left: int = Field(..., ge=0)
    purchased_at: date
    activated_at: Optional[date] = None


class GetUserTrainerWithPassword(GetUserWithId):
    trainer_profile: Optional[TrainerBaseWithPassword] = None
    blocked_at: Optional[datetime] = None
    active_membership: Optional[ActiveClientMembership] = None
    active_package: Optional[ActiveUserTrainerPackage] = None

class GetTrainer(TrainerBase):
    user: GetUserWithId = None
    rating: Optional[float] = Field(default=None, ge=1, le=5)
    model_config = ConfigDict(from_attributes=True)


class UsersCount(BaseModel):
    total: int = 0
    clients: int = 0
    trainers: int = 0
    gym_admins: int = 0


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole


class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[UserRole] = None


class UserUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=255)
    last_name: Optional[str] = Field(None, min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8)
    phone: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, min_length=1, max_length=255)


class UserBlock(BaseModel):
    comment: Optional[str] = Field(None, max_length=255)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
