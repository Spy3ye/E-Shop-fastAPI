from odmantic import Model
from typing import Optional
# from bson import ObjectId

class Product(Model):
    name: str
    description: Optional[str]
    price: float
    quantity: int
    category: Optional[str]
    image_url: Optional[str]

    class Config:
        collection = "products"
