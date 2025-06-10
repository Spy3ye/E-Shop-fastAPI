from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, List
from app.api_schemas.order import OrderOut
from app.api_schemas.product import ProductOut

def place_order(
    carts_collection: Collection,
    products_collection: Collection,
    orders_collection: Collection,
    user_id: str
) -> OrderOut:
    cart = carts_collection.find_one({"user_id": user_id})
    if not cart or not cart.get("items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    total = 0.0
    product_ids: List[str] = []

    for item in cart["items"]:
        product_id = item["product_id"]
        quantity = item["quantity"]

        if not ObjectId.is_valid(product_id):
            raise HTTPException(status_code=400, detail="Invalid product ID")

        product = products_collection.find_one({"_id": ObjectId(product_id)})
        if not product or product["quantity"] < quantity:
            raise HTTPException(status_code=400, detail="Not enough stock for one or more products")

        total += product["price"] * quantity

        # Update product quantity
        products_collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$inc": {"quantity": -quantity}}
        )

        product_ids.append(product_id)

    # Create order
    order_data = {
        "user_id": user_id,
        "product_ids": product_ids,
        "total_price": total,
        "status": "pending",
        "created_at": datetime.utcnow()
    }

    result = orders_collection.insert_one(order_data)
    order_data["_id"] = result.inserted_id

    # Clear cart
    carts_collection.update_one(
        {"user_id": user_id},
        {"$set": {"items": []}}
    )

    return OrderOut(**order_data, id=str(order_data["_id"]))
