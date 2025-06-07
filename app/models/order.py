# from odmantic import Model, Reference
from beanie import document
from uuid import UUID,uuid4
from pydantic import Field
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

class Order(document):
    order_Id : UUID = Field(default_factory=uuid4)
    user: User
    products: List[Product]
    total_price: float
    status: str = OrderStatus.PENDING
    created_at: datetime = datetime.now()

    class Settings:
        name = "orders"
