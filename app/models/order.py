# from odmantic import Model, Reference
from beanie import Document
from uuid import UUID,uuid4
from pydantic import Field,ConfigDict
from enum import Enum
from typing import List
# from bson import ObjectId
from datetime import datetime
from app.models.user import User
from app.models.product import Product

class OrderStatus(str,Enum):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Document):
    order_Id : UUID = Field(default_factory=uuid4)
    user: User
    products: List[Product]
    total_price: float
    status: str = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(from_attributes=True)
