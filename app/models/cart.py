from odmantic import Model, Reference
from typing import List, Optional
from pydantic import BaseModel
# from bson import ObjectId
from app.models.user import User
from app.models.product import Product

class CartItem(Model):
    product: Product = Reference()
    quantity: int

    class Config:
        collection = "cart_items"

class Cart(Model):
    user: User = Reference()
    items: List[CartItem] = []
    updated_at: Optional[str] = None

    class Config:
        collection = "carts"
