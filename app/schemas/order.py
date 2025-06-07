from pydantic import BaseModel
from typing import List
from datetime import datetime

class OrderCreate(BaseModel):
    product_ids: List[str]  # IDs of products
    total_price: float

class OrderOut(BaseModel):
    id: str
    user_id: str
    product_ids: List[str]
    total_price: float
    status: str
    created_at: datetime.now

    class Config:
        orm_mode = True
