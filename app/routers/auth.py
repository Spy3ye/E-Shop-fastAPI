from fastapi import APIRouter, Depends
from pymongo import MongoClient
from pymongo.database import Database
from app.api_schemas.token import Token
from app.api_schemas.user import UserLogin
from app.services.auth_services import login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

def get_database() -> Database:
    """Dependency to get MongoDB database connection"""
    # Replace with your actual MongoDB connection string
    client = MongoClient("mongodb://localhost:27017")
    return client.your_database_name  # Replace with your actual database name

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Database = Depends(get_database)):
    return await login_user(db, credentials)