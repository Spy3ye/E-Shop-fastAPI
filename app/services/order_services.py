# services/order_service.py
from odmantic import AIOEngine
from app.models.order import Order
from app.models.cart import Cart
from app.models.product import Product
from app.api_schemas.order import OrderOut
from fastapi import HTTPException
from datetime import datetime

async def place_order(engine: AIOEngine, user_id: str) -> OrderOut:
    cart = await engine.find_one(Cart, Cart.user_id == user_id)
    if not cart or not cart.items:
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0.0
    product_ids = []

    for item in cart.items:
        product = await engine.find_one(Product, Product.id == item.product_id)
        if product and product.quantity >= item.quantity:
            total += product.price * item.quantity
            product.quantity -= item.quantity
            await engine.save(product)
            product_ids.append(str(product.id))
        else:
            raise HTTPException(status_code=400, detail="Not enough stock for one or more products")

    order = Order(
        user_id=user_id,
        product_ids=product_ids,
        total_price=total,
        status="pending",
        created_at=datetime.utcnow()
    )
    await engine.save(order)

    # clear cart
    cart.items = []
    await engine.save(cart)

    return OrderOut.model_validate(order)
