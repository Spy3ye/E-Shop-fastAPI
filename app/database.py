import os
from typing import Dict, Any
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client: AsyncIOMotorClient | None = None
        self.db: AsyncIOMotorDatabase | None = None
        self.database_name = os.getenv("DATABASE_NAME")

    def connect(self) -> bool:
        """Initialize Motor client and database instance synchronously."""
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri or not self.database_name:
                logger.error("Mongo URI or DATABASE_NAME environment variables not set.")
                return False
            
            self.client = AsyncIOMotorClient(mongo_uri)
            self.db = self.client[self.database_name]

            logger.info("✅ Successfully connected to MongoDB")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False

    async def initialize(self) -> bool:
        """Async initialization: connect, create indexes, verify connection."""
        if not self.connect():
            return False
        
        try:
            await self.create_indexes()
            if not await self.verify_connection():
                return False
            
            logger.info("🎉 Database initialized successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False

    async def verify_connection(self) -> bool:
        """Ping the MongoDB server to verify connection."""
        if not self.db:
            logger.error("Database is not connected.")
            return False
        
        try:
            # Motor uses await for db commands
            await self.db.command("ping")
            logger.info("✅ Database verification successful")
            return True
        except Exception as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False

    async def create_indexes(self) -> None:
        """Create indexes on collections asynchronously."""
        if not self.db:
            raise RuntimeError("Database is not connected")
        
        logger.info("🔧 Creating database indexes...")
        
        # Users indexes
        try:
            users = self.db["users"]
            await users.create_index("email", unique=True, name="email_unique")
            await users.create_index("username", unique=True, name="username_unique")
            await users.create_index("created_at", name="created_at_idx")
            await users.create_index("is_active", name="is_active_idx")
            logger.info("✅ Users indexes created")
        except Exception as e:
            logger.warning(f"Users indexes creation warning: {e}")

        # Products indexes
        try:
            products = self.db["products"]
            await products.create_index("name", name="name_idx")
            await products.create_index("category", name="category_idx")
            await products.create_index("price", name="price_idx")
            await products.create_index("is_active", name="product_active_idx")
            await products.create_index("created_at", name="product_created_idx")
            await products.create_index("stock_quantity", name="stock_idx")
            await products.create_index([("name", "text"), ("description", "text")], name="search_text")
            await products.create_index([("category", 1), ("price", 1)], name="category_price_idx")
            logger.info("✅ Products indexes created")
        except Exception as e:
            logger.warning(f"Products indexes creation warning: {e}")

        # Orders indexes
        try:
            orders = self.db["orders"]
            await orders.create_index("user_id", name="user_orders_idx")
            await orders.create_index("status", name="order_status_idx")
            await orders.create_index("created_at", name="order_created_idx")
            await orders.create_index([("user_id", 1), ("created_at", -1)], name="user_orders_date_idx")
            await orders.create_index([("status", 1), ("created_at", -1)], name="status_date_idx")
            logger.info("✅ Orders indexes created")
        except Exception as e:
            logger.warning(f"Orders indexes creation warning: {e}")

        # Cart indexes
        try:
            cart = self.db["cart"]
            await cart.create_index("user_id", unique=True, name="user_cart_unique")
            await cart.create_index("updated_at", name="cart_updated_idx")
            logger.info("✅ Cart indexes created")
        except Exception as e:
            logger.warning(f"Cart indexes creation warning: {e}")

        # Order Items indexes
        try:
            order_items = self.db["order_items"]
            await order_items.create_index("order_id", name="order_items_order_idx")
            await order_items.create_index("product_id", name="order_items_product_idx")
            await order_items.create_index([("order_id", 1), ("product_id", 1)], name="order_product_idx")
            logger.info("✅ Order Items indexes created")
        except Exception as e:
            logger.warning(f"Order Items indexes creation warning: {e}")

        # Sessions indexes
        try:
            sessions = self.db["sessions"]
            await sessions.create_index("token", unique=True, name="token_unique")
            await sessions.create_index("user_id", name="session_user_idx")
            await sessions.create_index("expires_at", expireAfterSeconds=0, name="session_ttl")
            logger.info("✅ Sessions indexes created")
        except Exception as e:
            logger.warning(f"Sessions indexes creation warning: {e}")

        # Categories indexes
        try:
            categories = self.db["categories"]
            await categories.create_index("name", unique=True, name="category_name_unique")
            await categories.create_index("slug", unique=True, name="category_slug_unique")
            await categories.create_index("is_active", name="category_active_idx")
            logger.info("✅ Categories indexes created")
        except Exception as e:
            logger.warning(f"Categories indexes creation warning: {e}")

        logger.info("🎉 All database indexes created successfully!")

    async def disconnect(self) -> None:
        """Close the MongoDB connection asynchronously."""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")

    # Collections getter methods (sync, since Motor collections are async ready)
    def get_collection(self, name: str):
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db[name]

    @property
    def users(self):
        return self.get_collection("users")

    @property
    def products(self):
        return self.get_collection("products")

    @property
    def orders(self):
        return self.get_collection("orders")

    @property
    def cart(self):
        return self.get_collection("cart")

    @property
    def order_items(self):
        return self.get_collection("order_items")

    @property
    def sessions(self):
        return self.get_collection("sessions")

    @property
    def categories(self):
        return self.get_collection("categories")

    async def health_check(self) -> Dict[str, Any]:
        """Check database health asynchronously and return status"""
        if not self.client or not self.db:
            return {"status": "unhealthy", "error": "Not connected", "connection": "failed"}

        try:
            await self.db.command("ping")
            stats = await self.db.command("dbStats")
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "connection": "active",
            }
        except Exception as e:
            return {"status": "unhealthy", "error": str(e), "connection": "failed"}

    async def get_database_info(self) -> Dict[str, Any]:
        """Get detailed database info asynchronously"""
        if not self.client or not self.db:
            return {"error": "Not connected"}

        try:
            server_info = await self.client.server_info()
            db_stats = await self.db.command("dbStats")
            collections = await self.db.list_collection_names()
            collection_stats = {}

            for collection_name in collections:
                try:
                    stats = await self.db.command("collStats", collection_name)
                    collection_stats[collection_name] = {
                        "count": stats.get("count", 0),
                        "size": stats.get("size", 0),
                        "avgObjSize": stats.get("avgObjSize", 0),
                        "totalIndexSize": stats.get("totalIndexSize", 0),
                        "nindexes": stats.get("nindexes", 0),
                    }
                except Exception:
                    collection_stats[collection_name] = {"error": "Could not get stats"}

            return {
                "server_version": server_info.get("version"),
                "database_name": self.database_name,
                "collections": collections,
                "collection_stats": collection_stats,
                "database_stats": {
                    "collections": db_stats.get("collections", 0),
                    "objects": db_stats.get("objects", 0),
                    "data_size": db_stats.get("dataSize", 0),
                    "storage_size": db_stats.get("storageSize", 0),
                    "indexes": db_stats.get("indexes", 0),
                    "index_size": db_stats.get("indexSize", 0),
                },
            }
        except Exception as e:
            return {"error": str(e)}


# Global instance
database = DatabaseManager()

# Convenience async functions for external use

async def create_tables() -> bool:
    return await database.initialize()

async def get_database() -> AsyncIOMotorDatabase:
    if not database.db:
        raise RuntimeError("Database not initialized")
    return database.db

async def check_database_health() -> Dict[str, Any]:
    return await database.health_check()

# Export collections (sync properties)
def get_users_collection():
    return database.users

def get_products_collection():
    return database.products

def get_orders_collection():
    return database.orders

def get_cart_collection():
    return database.cart

def get_order_items_collection():
    return database.order_items

def get_sessions_collection():
    return database.sessions

def get_categories_collection():
    return database.categories
