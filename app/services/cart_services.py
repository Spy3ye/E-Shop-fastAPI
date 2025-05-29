# services/cart_service.py
from odmantic import AIOEngine
from models.cart import Cart, CartItem
from models.product import Product
from schemas.cart import CartOut, CartItemOut
from fastapi import HTTPException

async def get_or_create_cart(engine: AIOEngine, user_id: str) -> Cart:
    cart = await engine.find_one(Cart, Cart.user_id == user_id)
    if not cart:
        cart = Cart(user_id=user_id, items=[])
        await engine.save(cart)
    return cart

async def add_item_to_cart(engine: AIOEngine, user_id: str, product_id: str, quantity: int) -> CartOut:
    product = await engine.find_one(Product, Product.id == product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = await get_or_create_cart(engine, user_id)

    # update quantity if item exists
    for item in cart.items:
        if item.product_id == product_id:
            item.quantity += quantity
            break
    else:
        cart.items.append(CartItem(product_id=product_id, quantity=quantity))

    await engine.save(cart)

    # return enriched cart
    return await build_cart_out(engine, cart)

async def build_cart_out(engine: AIOEngine, cart: Cart) -> CartOut:
    enriched_items = []
    for item in cart.items:
        product = await engine.find_one(Product, Product.id == item.product_id)
        if product:
            enriched_items.append(CartItemOut(product=product, quantity=item.quantity))
    
    return CartOut(id=str(cart.id), user_id=cart.user_id, items=enriched_items)
