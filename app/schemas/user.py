from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from app.models.user import UserRole
from app.schemas.gym import GetGym, GetGymApplication


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


class UserResponse(UserBase):
    id: str
    created_at: datetime
    blocked_at: Optional[datetime] = None
    blocked_comment: Optional[str] = None
    deleted_at: Optional[datetime] = None

    avatar: Optional[AvatarResponse] = None

    gym_application: Optional[GetGymApplication] = None
    gym: Optional[GetGym] = None

    model_config = ConfigDict(from_attributes=True)


class UsersCount(BaseModel):
    total: int = 0
    clients: int = 0
    trainers: int = 0
    gym_admins: int = 0


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


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