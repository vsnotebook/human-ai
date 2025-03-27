from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserUpdate(UserBase):
    password: Optional[str] = Field(None, min_length=6)

class UserInDB(UserBase):
    id: str
    role: str = "user"
    trial_count: int = 10
    trial_seconds: int = 60
    remaining_minutes: int = 0
    subscription_expiry: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        from_attributes = True