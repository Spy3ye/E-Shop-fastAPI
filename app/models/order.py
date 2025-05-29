from odmantic import Model, Reference
from typing import List
# from bson import ObjectId
from datetime import datetime
from app.models.user import User
from app.models.product import Product

class OrderStatus(str):
    PENDING = "pending"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(Model):
    user: User = Reference()
    products: List[Product] = Reference()
    total_price: float
    status: str = OrderStatus.PENDING
    created_at: datetime = datetime.utcnow()

    class Config:
        collection = "orders"
