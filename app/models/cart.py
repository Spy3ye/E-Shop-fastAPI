# from odmantic import Model, Reference
from beanie import document
from typing import List, Optional
from uuid import UUID,uuid4
from pydantic import Field
# from bson import ObjectId
from app.models.user import User
from app.models.product import Product

class CartItem(document):
    product: Product
    quantity: int

    class Settings:
        name = "cart_items"

class Cart(document):
    cart_Id : UUID = Field(default_factory=uuid4)
    user: User
    items: List[CartItem] = []
    updated_at: Optional[str] = None

    class Settings:
        name = "carts"
