from fastapi import APIRouter, Depends
from pymongo.database import Database
from app.api_schemas.user import UserCreate, UserOut
from app.services.user_services import UserServices
from app.database import get_db # You'll need to create this dependency

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut)
async def register_user(user_data: UserCreate, db: Database = Depends(get_db)):
    return await UserServices.create_user(db, user_data)