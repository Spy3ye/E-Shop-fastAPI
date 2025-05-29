from pydantic import BaseModel
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

    class Config:
        orm_mode = True
