# from odmantic import Model, Reference
from beanie import Document
from typing import List, Optional
from uuid import UUID,uuid4
from pydantic import Field , ConfigDict
# from bson import ObjectId
from app.models.user import User
from app.models.product import Product

class CartItem(Document):
    product: Product
    quantity: int

    model_config = ConfigDict(from_attributes=True)

class Cart(Document):
    cart_Id : UUID = Field(default_factory=uuid4)
    user: User
    items: List[CartItem] = []
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
