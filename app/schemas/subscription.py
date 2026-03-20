from pydantic import BaseModel, Field


class EditSubscriptionText(BaseModel):
    description: str = Field(...)
