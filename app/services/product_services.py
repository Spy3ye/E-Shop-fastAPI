from pymongo import MongoClient
from bson import ObjectId
from fastapi import HTTPException
from app.api_schemas.product import ProductCreate, ProductOut

# Utility function to convert MongoDB document to Pydantic model
def product_out_from_doc(doc: dict) -> ProductOut:
    # Convert Mongo ObjectId to str and map to Pydantic model
    doc["id"] = str(doc["_id"])
    doc.pop("_id", None)
    return ProductOut.model_validate(doc)

async def create_product(db, data: ProductCreate) -> ProductOut:
    # data is a Pydantic model; convert to dict and insert
    product_dict = data.model_dump()
    result = db.products.insert_one(product_dict)  # Insert into 'products' collection
    product_doc = db.products.find_one({"_id": result.inserted_id})
    return product_out_from_doc(product_doc)

async def get_product(db, product_id: str) -> ProductOut:
    # Validate ObjectId format
    if not ObjectId.is_valid(product_id):
        raise HTTPException(status_code=400, detail="Invalid product ID format")
    product_doc = db.products.find_one({"_id": ObjectId(product_id)})
    if not product_doc:
        raise HTTPException(status_code=404, detail="Product not found")
    return product_out_from_doc(product_doc)

async def list_products(db) -> list[ProductOut]:
    cursor = db.products.find()
    products = []
    async for doc in cursor:  # pymongo does NOT support async, so you can remove async here
        products.append(product_out_from_doc(doc))
    return products
