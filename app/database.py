import os
from typing import Dict, Any
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, TEXT
from pymongo.errors import PyMongoError
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.client: MongoClient | None = None
        self.db = None
        self.database_name = os.getenv("DATABASE_NAME")

    def connect(self) -> bool:
        """Initialize PyMongo client and database instance."""
        try:
            mongo_uri = os.getenv("MONGO_URI")
            if not mongo_uri or not self.database_name:
                logger.error("Mongo URI or DATABASE_NAME environment variables not set.")
                return False

            self.client = MongoClient(mongo_uri)
            self.db = self.client[self.database_name]

            logger.info("✅ Successfully connected to MongoDB")
            return True
        except PyMongoError as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False

    def initialize(self) -> bool:
        """Initialize database and create indexes."""
        if not self.connect():
            return False

        try:
            self.create_indexes()
            if not self.verify_connection():
                return False
            logger.info("🎉 Database initialized successfully!")
            return True
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            return False

    def verify_connection(self) -> bool:
        """Ping the MongoDB server to verify connection."""
        if not self.db:
            logger.error("Database is not connected.")
            return False

        try:
            self.db.command("ping")
            logger.info("✅ Database verification successful")
            return True
        except PyMongoError as e:
            logger.error(f"❌ Database verification failed: {e}")
            return False

    def create_indexes(self) -> None:
        """Create indexes on collections."""
        if not self.db:
            raise RuntimeError("Database is not connected")

        logger.info("🔧 Creating database indexes...")

        try:
            self.db["users"].create_index("email", unique=True, name="email_unique")
            self.db["users"].create_index("username", unique=True, name="username_unique")
            self.db["users"].create_index("created_at", name="created_at_idx")
            self.db["users"].create_index("is_active", name="is_active_idx")
            logger.info("✅ Users indexes created")
        except PyMongoError as e:
            logger.warning(f"Users indexes creation warning: {e}")

        try:
            self.db["products"].create_index("name", name="name_idx")
            self.db["products"].create_index("category", name="category_idx")
            self.db["products"].create_index("price", name="price_idx")
            self.db["products"].create_index("is_active", name="product_active_idx")
            self.db["products"].create_index("created_at", name="product_created_idx")
            self.db["products"].create_index("stock_quantity", name="stock_idx")
            self.db["products"].create_index([("name", TEXT), ("description", TEXT)], name="search_text")
            self.db["products"].create_index([("category", ASCENDING), ("price", ASCENDING)], name="category_price_idx")
            logger.info("✅ Products indexes created")
        except PyMongoError as e:
            logger.warning(f"Products indexes creation warning: {e}")

        try:
            self.db["orders"].create_index("user_id", name="user_orders_idx")
            self.db["orders"].create_index("status", name="order_status_idx")
            self.db["orders"].create_index("created_at", name="order_created_idx")
            self.db["orders"].create_index([("user_id", ASCENDING), ("created_at", -1)], name="user_orders_date_idx")
            self.db["orders"].create_index([("status", ASCENDING), ("created_at", -1)], name="status_date_idx")
            logger.info("✅ Orders indexes created")
        except PyMongoError as e:
            logger.warning(f"Orders indexes creation warning: {e}")

        try:
            self.db["cart"].create_index("user_id", unique=True, name="user_cart_unique")
            self.db["cart"].create_index("updated_at", name="cart_updated_idx")
            logger.info("✅ Cart indexes created")
        except PyMongoError as e:
            logger.warning(f"Cart indexes creation warning: {e}")

        try:
            self.db["order_items"].create_index("order_id", name="order_items_order_idx")
            self.db["order_items"].create_index("product_id", name="order_items_product_idx")
            self.db["order_items"].create_index([("order_id", ASCENDING), ("product_id", ASCENDING)], name="order_product_idx")
            logger.info("✅ Order Items indexes created")
        except PyMongoError as e:
            logger.warning(f"Order Items indexes creation warning: {e}")

        try:
            self.db["sessions"].create_index("token", unique=True, name="token_unique")
            self.db["sessions"].create_index("user_id", name="session_user_idx")
            self.db["sessions"].create_index("expires_at", expireAfterSeconds=0, name="session_ttl")
            logger.info("✅ Sessions indexes created")
        except PyMongoError as e:
            logger.warning(f"Sessions indexes creation warning: {e}")

        try:
            self.db["categories"].create_index("name", unique=True, name="category_name_unique")
            self.db["categories"].create_index("slug", unique=True, name="category_slug_unique")
            self.db["categories"].create_index("is_active", name="category_active_idx")
            logger.info("✅ Categories indexes created")
        except PyMongoError as e:
            logger.warning(f"Categories indexes creation warning: {e}")

        logger.info("🎉 All database indexes created successfully!")

    def disconnect(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")

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

    def health_check(self) -> Dict[str, Any]:
        """Check database health and return status"""
        if not self.client or not self.db:
            return {"status": "unhealthy", "error": "Not connected", "connection": "failed"}

        try:
            self.db.command("ping")
            stats = self.db.command("dbStats")
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "connection": "active",
            }
        except PyMongoError as e:
            return {"status": "unhealthy", "error": str(e), "connection": "failed"}

    def get_database_info(self) -> Dict[str, Any]:
        """Get detailed database info"""
        if not self.client or not self.db:
            return {"error": "Not connected"}

        try:
            server_info = self.client.server_info()
            db_stats = self.db.command("dbStats")
            collections = self.db.list_collection_names()
            collection_stats = {}

            for collection_name in collections:
                try:
                    stats = self.db.command("collStats", collection_name)
                    collection_stats[collection_name] = {
                        "count": stats.get("count", 0),
                        "size": stats.get("size", 0),
                        "avgObjSize": stats.get("avgObjSize", 0),
                        "totalIndexSize": stats.get("totalIndexSize", 0),
                        "nindexes": stats.get("nindexes", 0),
                    }
                except PyMongoError:
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
        except PyMongoError as e:
            return {"error": str(e)}


# Global instance
database = DatabaseManager()

# External utility functions

def create_tables() -> bool:
    return database.initialize()

def get_db():
    if not database.db:
        raise RuntimeError("Database not initialized")
    return database.db

def check_database_health() -> Dict[str, Any]:
    return database.health_check()

# Collection accessors
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
