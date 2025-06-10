from fastapi import APIRouter, Depends
from pymongo import MongoClient
from pymongo.database import Database
from app.api_schemas.cart import CartOut
from app.services.cart_services import add_item_to_cart, build_cart_out, get_or_create_cart

router = APIRouter(prefix="/cart", tags=["Cart"])

def get_database() -> Database:
    """Dependency to get MongoDB database connection"""
    # Replace with your actual MongoDB connection string
    client = MongoClient("mongodb://localhost:27017")
    return client.your_database_name  # Replace with your actual database name

@router.post("/add", response_model=CartOut)
async def add_item(user_id: str, product_id: str, quantity: int, db: Database = Depends(get_database)):
    return await add_item_to_cart(db, user_id, product_id, quantity)

@router.get("/", response_model=CartOut)
async def view_cart(user_id: str, db: Database = Depends(get_database)):
    cart = await get_or_create_cart(db, user_id)
    return await build_cart_out(db, cart)