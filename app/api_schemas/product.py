from pydantic import BaseModel,ConfigDict
from typing import Optional

class ProductCreate(BaseModel):
    name: str
    description: Optional[str]
    price: float
    quantity: int
    category: Optional[str]
    image_url: Optional[str]

class ProductOut(ProductCreate):
    id: str
    name: str
    price: float
    category: Optional[str]

    model_config = ConfigDict(from_attributes=True)
