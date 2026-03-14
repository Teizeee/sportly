from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date
from typing import Optional
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    first_name: str = Field(..., min_length=1, max_length=255)
    last_name: str = Field(..., min_length=1, max_length=255)
    patronymic: Optional[str] = Field(None, max_length=255)
    birth_date: Optional[date] = None
    role: UserRole = UserRole.CLIENT


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    blocked_at: Optional[datetime] = None
    blocked_comment: Optional[str] = None
    deleted_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


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


class UserBlock(BaseModel):
    comment: Optional[str] = Field(None, max_length=255)


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)