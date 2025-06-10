from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.api_schemas.cart import CartOut
from app.services.cart_services import add_item_to_cart, build_cart_out, get_or_create_cart
from app.database import get_db

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add", response_model=CartOut)
def add_item(
    user_id: str,
    product_id: str,
    quantity: int,
    db: Database = Depends(get_db),  # ✅ use PyMongo db
):
    return add_item_to_cart(db, user_id, product_id, quantity)

@router.get("/", response_model=CartOut)
def view_cart(
    user_id: str,
    db: Database = Depends(get_db),  # ✅ use PyMongo db
):
    cart = get_or_create_cart(db, user_id)
    return build_cart_out(db, cart)
