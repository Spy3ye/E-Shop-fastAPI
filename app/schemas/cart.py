# app/schemas/cart.py

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)

class CartItemCreate(CartItemBase):
    pass

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)

class CartItem(CartItemBase):
    id: int
    cart_id: int
    added_at: datetime
    
    class Config:
        from_attributes = True

class CartItemWithProduct(CartItem):
    product_name: str
    product_price: float
    product_image_url: Optional[str] = None

class Cart(BaseModel):
    id: int
    user_id: int
    items: List[CartItemWithProduct]
    total_price: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True