from pydantic import BaseModel
from typing import List

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int

class CartItemOut(BaseModel):
    id: str
    product_id: str
    name: str
    quantity: int

    class Config:
        orm_mode = True

class CartCreate(BaseModel):
    items: List[CartItemCreate]

class CartOut(BaseModel):
    id: str
    user_id: str
    items: List[CartItemOut]

    class Config:
        orm_mode = True
