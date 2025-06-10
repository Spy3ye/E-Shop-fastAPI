from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.api_schemas.product import ProductCreate, ProductOut
from app.services.product_services import create_product, get_product, list_products
from app.database import get_database  # You'll need to create this dependency

router = APIRouter(prefix="/products", tags=["Products"])

@router.post("/", response_model=ProductOut)
async def create(data: ProductCreate, db: Database = Depends(get_database)):
    return await create_product(db, data)

@router.get("/{product_id}", response_model=ProductOut)
async def retrieve(product_id: str, db: Database = Depends(get_database)):
    return await get_product(db, product_id)

@router.get("/", response_model=list[ProductOut])
async def list_all(db: Database = Depends(get_database)):
    return await list_products(db)