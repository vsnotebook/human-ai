from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class OrderBase(BaseModel):
    plan_id: str
    amount: float
    minutes: int
    duration: int

class OrderCreate(OrderBase):
    user_id: str
    payment_method: str

class OrderInDB(OrderBase):
    id: str
    user_id: str
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)
    paid_at: Optional[datetime] = None

    class Config:
        from_attributes = True