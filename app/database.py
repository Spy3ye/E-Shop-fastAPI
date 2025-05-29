from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGODB_URL, DATABASE_NAME

class Database:
    client: AsyncIOMotorClient = None
    database = None

database = Database()

async def connect_to_mongo():
    """Create database connection"""
    database.client = AsyncIOMotorClient(MONGODB_URL)
    database.database = database.client[DATABASE_NAME]
    print(f"Connected to MongoDB at {MONGODB_URL}")

async def close_mongo_connection():
    """Close database connection"""
    if database.client:
        database.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return database.database

# Collection getters
def get_users_collection():
    return get_database().users

def get_products_collection():
    return get_database().products

def get_orders_collection():
    return get_database().orders

def get_categories_collection():
    return get_database().categories