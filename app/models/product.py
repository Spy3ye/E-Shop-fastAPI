# from odmantic import Model
from uuid import UUID,uuid4
from pydantic import Field
from beanie import document
from typing import Optional
# from bson import ObjectId

class Product(document):
    product_Id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str]
    price: float
    quantity: int
    category: Optional[str]
    image_url: Optional[str]

    class Settings:
        name = "products"
