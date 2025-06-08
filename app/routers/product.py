from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from app.api_schemas.product import ProductCreate, ProductOut
from app.services.product_services import create_product, get_product, list_products

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductOut)
async def create(data: ProductCreate, engine: AIOEngine = Depends()):
    return await create_product(engine, data)

@router.get("/{product_id}", response_model=ProductOut)
async def retrieve(product_id: str, engine: AIOEngine = Depends()):
    return await get_product(engine, product_id)

@router.get("/", response_model=list[ProductOut])
async def list_all(engine: AIOEngine = Depends()):
    return await list_products(engine)
