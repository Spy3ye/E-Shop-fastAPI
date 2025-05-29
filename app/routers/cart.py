from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from schemas.cart import CartOut
from services.cart_services import add_item_to_cart, build_cart_out, get_or_create_cart

router = APIRouter(prefix="/cart", tags=["Cart"])

@router.post("/add", response_model=CartOut)
async def add_item(user_id: str, product_id: str, quantity: int, engine: AIOEngine = Depends()):
    return await add_item_to_cart(engine, user_id, product_id, quantity)

@router.get("/", response_model=CartOut)
async def view_cart(user_id: str, engine: AIOEngine = Depends()):
    cart = await get_or_create_cart(engine, user_id)
    return await build_cart_out(engine, cart)
