# services/product_service.py
from odmantic import AIOEngine
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductOut
from fastapi import HTTPException

async def create_product(engine: AIOEngine, data: ProductCreate) -> ProductOut:
    product = Product(**data.model_dump())
    await engine.save(product)
    return ProductOut.model_validate(product)

async def get_product(engine: AIOEngine, product_id: str) -> ProductOut:
    product = await engine.find_one(Product, Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.model_validate(product)

async def list_products(engine: AIOEngine) -> list[ProductOut]:
    products = await engine.find(Product)
    return [ProductOut.model_validate(p) for p in products]
