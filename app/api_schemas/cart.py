from pydantic import BaseModel , ConfigDict
from typing import List

class CartItemCreate(BaseModel):
    product_id: str
    quantity: int

class CartItemOut(BaseModel):
    id: str
    product_id: str
    name: str
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class CartCreate(BaseModel):
    items: List[CartItemCreate]

class CartOut(BaseModel):
    id: str
    user_id: str
    items: List[CartItemOut]

    model_config = ConfigDict(from_attributes=True)
