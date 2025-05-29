# app/schemas/order.py

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Order status enum
class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

# OrderItem schemas
class OrderItemBase(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    order_id: int

    class Config:
        from_attributes = True

# Order schemas
class OrderBase(BaseModel):
    shipping_address: str
    payment_method: str
    total_amount: Optional[float] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    shipping_address: Optional[str] = None
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    payment_id: Optional[str] = None
    tracking_number: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[OrderItem]
    total_amount: float

    class Config:
        from_attributes = True

class OrderList(BaseModel):
    items: List[Order]
    total: int
    page: int
    page_size: int
    pages: int