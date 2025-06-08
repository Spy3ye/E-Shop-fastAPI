# from odmantic import Model
from uuid import UUID,uuid4
from pydantic import Field , ConfigDict
from beanie import Document
from typing import Optional
# from bson import ObjectId

class Product(Document):
    product_Id: UUID = Field(default_factory=uuid4)
    name: str
    description: Optional[str]
    price: float
    quantity: int
    category: Optional[str]
    image_url: Optional[str]

    model_config = ConfigDict(from_attributes=True)
