from bson import ObjectId
from pymongo.collection import Collection
from fastapi import HTTPException
from typing import List, Dict
from app.api_schemas.cart import CartOut, CartItemOut
from app.api_schemas.product import ProductOut
from app.models.cart import CartItem
from app.models.product import Product

def get_or_create_cart(carts_collection: Collection, user_id: str) -> Dict:
    cart = carts_collection.find_one({"user_id": user_id})
    if not cart:
        cart = {
            "user_id": user_id,
            "items": []
        }
        result = carts_collection.insert_one(cart)
        cart["_id"] = result.inserted_id
    return cart

def add_item_to_cart(carts_collection: Collection, products_collection: Collection, user_id: str, product_id: str, quantity: int) -> CartOut:
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID")

    product = products_collection.find_one({"_id": ObjectId(product_id)})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = get_or_create_cart(carts_collection, user_id)

    # Update or add item
    for item in cart["items"]:
        if item["product_id"] == product_id:
            item["quantity"] += quantity
            break
    else:
        cart["items"].append({"product_id": product_id, "quantity": quantity})

    carts_collection.update_one({"_id": cart["_id"]}, {"$set": {"items": cart["items"]}})

    return build_cart_out(products_collection, cart)

def build_cart_out(products_collection: Collection, cart: Dict) -> CartOut:
    enriched_items: List[CartItemOut] = []

    for item in cart["items"]:
        product = products_collection.find_one({"_id": ObjectId(item["product_id"])})
        if product:
            product_out = ProductOut(**product, id=str(product["_id"]))
            enriched_items.append(CartItemOut(product=product_out, quantity=item["quantity"]))

    return CartOut(id=str(cart["_id"]), user_id=cart["user_id"], items=enriched_items)
