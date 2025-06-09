# app/main.py

from fastapi import FastAPI,HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.routers import user, product, order, auth, cart
from app.database import DatabaseManager

app = FastAPI(
    title="E-Commerce API",
    description="Backend API for an E-Commerce Platform",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["GET" , "POST" , "PUT" , "DELETE"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["Authentication"], prefix="/api/auth")
app.include_router(user.router, tags=["Users"], prefix="/api/users")
app.include_router(product.router, tags=["Products"], prefix="/api/products")
app.include_router(order.router, tags=["Orders"], prefix="/api/orders")
app.include_router(cart.router, tags=["Shopping Cart"], prefix="/api/cart")

@app.on_event("startup")
async def startup_event():
    """Initialize database on application startup"""
    db_manager = DatabaseManager()
    success = db_manager.initialize()  # This calls database.initialize()
    if not success:
        raise HTTPException("Failed to initialize database")

@app.on_event("shutdown") 
async def shutdown_event():
    """Clean up database connections on shutdown"""
    db_manager = DatabaseManager()
    db_manager.disconnect()

# Health check endpoints
@app.get("/")
async def root():
    return {
        "message": "E-Commerce API is running!",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    health_info = DatabaseManager.health_check()
    return health_info

@app.get("/db-info")
async def database_info():
    """Get detailed database information"""
    return DatabaseManager.get_database_info()
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Welcome to the E-Commerce API"}

# Custom OpenAPI schema
# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
    
#     openapi_schema = get_openapi(
#         title="E-Commerce API",
#         version="1.0.0",
#         description="API for a modern e-commerce platform",
#         routes=app.routes,
#     )
    
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema

# app.openapi = custom_openapi