from pydantic import BaseModel, Field


class BaseGymApplication(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=255)
    description: str = Field(..., min_length=1, max_length=255)
    phone: str = Field(..., min_length=1, max_length=255)

class ApproveGymApplication(BaseModel):
    gym_application_id: str = Field(..., min_length=1, max_length=36)
    platform_subscription_id: str = Field(..., min_length=1, max_length=36)

class RejectGymApplication(BaseModel):
    comment: str = Field(..., min_length=1, max_length=255)
