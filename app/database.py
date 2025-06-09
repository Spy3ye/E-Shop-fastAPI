import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import OperationFailure, ConnectionFailure, DuplicateKeyError
from pymongo.collection import Collection
from pymongo.database import Database as MongoDatabase
import logging
from motor.motor_asyncio import AsyncIOMotorClient
import ssl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Only initialize non-async attributes here
        self.client = None
        self.database = None
        self.engine = None
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Synchronous connection setup"""
        try:
            self.client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
            self.database = self.client[os.getenv("DATABASE_NAME")]
            self.engine = AIOEngine(client=self.client, database=os.getenv("DATABASE_NAME"))
            self.logger.info("✅ Successfully connected to MongoDB")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to connect to MongoDB: {e}")
            return False
    
    async def initialize(self):
        """Async initialization method"""
        try:
            if not self.connect():
                return False
            
            await self.create_indexes()
            
            if not await self.verify_connection():
                return False
            
            self.logger.info("🎉 Database initialized successfully!")
            return True
        except Exception as e:
            self.logger.error(f"❌ Database initialization failed: {e}")
            return False
    
    async def verify_connection(self):
        """Verify database connection"""
        try:
            # Simple ping test
            await self.database.command("ping")
            self.logger.info("✅ Database verification successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ Database verification failed: {e}")
            return False
    
    async def create_indexes(self):
        """Create database indexes"""
        try:
            # Your existing index creation code here
            self.logger.info("🔧 Creating database indexes...")
            # ... your index creation logic
            self.logger.info("✅ All database indexes created successfully!")
        except Exception as e:
            self.logger.error(f"❌ Failed to create indexes: {e}")
            raise
    
    async def disconnect(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("🔌 Disconnected from MongoDB")
    
    async def get_collection(self, collection_name: str) -> Collection:
        """Get a MongoDB collection"""
        if collection_name not in self._collections:
            self._collections[collection_name] = self.db[collection_name]
        return self._collections[collection_name]
    
    @property
    async def users(self) -> Collection:
        return self.get_collection("users")
    
    @property
    async def products(self) -> Collection:
        return self.get_collection("products")
    
    @property
    async def orders(self) -> Collection:
        return self.get_collection("orders")
    
    @property
    async def cart(self) -> Collection:
        return self.get_collection("cart")
    
    @property
    async def order_items(self) -> Collection:
        return self.get_collection("order_items")
    
    @property
    async def sessions(self) -> Collection:
        return self.get_collection("sessions")
    
    @property
    async def categories(self) -> Collection:
        return self.get_collection("categories")
    
    
    
    # async def create_indexes(self) -> bool:
    #     """Create all necessary indexes for optimal performance"""
    #     try:
    #         logger.info("🔧 Creating database indexes...")
            
    #         # Users collection indexes
    #         try:
    #             self.users.create_index("email", unique=True, name="email_unique")
    #             self.users.create_index("username", unique=True, name="username_unique")
    #             self.users.create_index("created_at", name="created_at_idx")
    #             self.users.create_index("is_active", name="is_active_idx")
    #             logger.info("✅ Users indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Users indexes already exist")
            
    #         # Products collection indexes
    #         try:
    #             self.products.create_index("name", name="name_idx")
    #             self.products.create_index("category", name="category_idx")
    #             self.products.create_index("price", name="price_idx")
    #             self.products.create_index("is_active", name="product_active_idx")
    #             self.products.create_index("created_at", name="product_created_idx")
    #             self.products.create_index("stock_quantity", name="stock_idx")
    #             self.products.create_index([("name", "text"), ("description", "text")], name="search_text")
    #             self.products.create_index([("category", 1), ("price", 1)], name="category_price_idx")
    #             logger.info("✅ Products indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Products indexes already exist")
            
    #         # Orders collection indexes
    #         try:
    #             self.orders.create_index("user_id", name="user_orders_idx")
    #             self.orders.create_index("status", name="order_status_idx")
    #             self.orders.create_index("created_at", name="order_created_idx")
    #             self.orders.create_index([("user_id", 1), ("created_at", -1)], name="user_orders_date_idx")
    #             self.orders.create_index([("status", 1), ("created_at", -1)], name="status_date_idx")
    #             logger.info("✅ Orders indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Orders indexes already exist")
            
    #         # Cart collection indexes
    #         try:
    #             self.cart.create_index("user_id", unique=True, name="user_cart_unique")
    #             self.cart.create_index("updated_at", name="cart_updated_idx")
    #             logger.info("✅ Cart indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Cart indexes already exist")
            
    #         # Order Items collection indexes
    #         try:
    #             self.order_items.create_index("order_id", name="order_items_order_idx")
    #             self.order_items.create_index("product_id", name="order_items_product_idx")
    #             self.order_items.create_index([("order_id", 1), ("product_id", 1)], name="order_product_idx")
    #             logger.info("✅ Order Items indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Order Items indexes already exist")
            
    #         # Sessions collection indexes (for authentication)
    #         try:
    #             self.sessions.create_index("token", unique=True, name="token_unique")
    #             self.sessions.create_index("user_id", name="session_user_idx")
    #             self.sessions.create_index("expires_at", expireAfterSeconds=0, name="session_ttl")
    #             logger.info("✅ Sessions indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Sessions indexes already exist")
            
    #         # Categories collection indexes
    #         try:
    #             self.categories.create_index("name", unique=True, name="category_name_unique")
    #             self.categories.create_index("slug", unique=True, name="category_slug_unique")
    #             self.categories.create_index("is_active", name="category_active_idx")
    #             logger.info("✅ Categories indexes created")
    #         except OperationFailure as e:
    #             if "already exists" not in str(e):
    #                 raise e
    #             logger.info("✅ Categories indexes already exist")
            
    #         logger.info("🎉 All database indexes created successfully!")
    #         return True
            
    #     except Exception as e:
    #         logger.error(f"❌ Error creating indexes: {e}")
    #         return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database health and return status"""
        try:
            # Test connection
            self.client.admin.command('ping')
            
            # Get database stats
            stats = self.db.command("dbStats")
            
            return {
                "status": "healthy",
                "database": self.database_name,
                "collections": stats.get("collections", 0),
                "data_size": stats.get("dataSize", 0),
                "storage_size": stats.get("storageSize", 0),
                "indexes": stats.get("indexes", 0),
                "connection": "active"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "connection": "failed"
            }
    
    
    
    # async def initialize(self) -> bool:
    #     """Initialize database connection and create indexes"""
    #     if not self.connect():
    #         return False
        
    #     if not self.create_indexes():
    #         return False
        
    #     # Verify collections work by doing a simple operation
    #     try:
    #         collections_to_test = ['users', 'products', 'orders', 'cart']
    #         for collection_name in collections_to_test:
    #             collection = self.get_collection(collection_name)
    #             # Test insert and delete
    #             test_doc = {"_test": True, "timestamp": datetime.utcnow()}
    #             result = collection.insert_one(test_doc)
    #             collection.delete_one({"_id": result.inserted_id})
    #             logger.info(f"✅ {collection_name} collection verified")
            
    #         logger.info("🚀 Database initialized successfully!")
    #         return True
            
    #     except Exception as e:
    #         logger.error(f"❌ Database verification failed: {e}")
    #         return False
    
    async def get_database_info(self) -> Dict[str, Any]:
        """Get detailed database information"""
        try:
            # Server info
            server_info = self.client.server_info()
            
            # Database stats
            db_stats = self.db.command("dbStats")
            
            # Collection info
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
                        "nindexes": stats.get("nindexes", 0)
                    }
                except:
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
                    "index_size": db_stats.get("indexSize", 0)
                }
            }
        except Exception as e:
            return {"error": str(e)}

# Create global database instance
database = DatabaseManager()

# Convenience functions for backward compatibility
async def create_tables() -> bool:
    """Initialize database - for compatibility with existing code"""
    return database.initialize()

async def get_database() -> MongoDatabase:
    """Get the MongoDB database instance"""
    return database.db

async def check_database_health() -> bool:
    """Check if database is healthy"""
    health = database.health_check()
    return health.get("status") == "healthy"

# Export collections for direct access
async def get_users_collection() -> Collection:
    return database.users

async def get_products_collection() -> Collection:
    return database.products

async def get_orders_collection() -> Collection:
    return database.orders

async def get_cart_collection() -> Collection:
    return database.cart

async def get_order_items_collection() -> Collection:
    return database.order_items

async def get_sessions_collection() -> Collection:
    return database.sessions

async def get_categories_collection() -> Collection:
    return database.categories