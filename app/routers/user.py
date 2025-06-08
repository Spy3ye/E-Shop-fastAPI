from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from app.api_schemas.user import UserCreate, UserOut
from app.services.user_services import UserServices

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut)
async def register_user(user_data: UserCreate, engine: AIOEngine = Depends()):
    return await UserServices.create_user(engine, user_data)
