from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from schemas.user import UserCreate, UserOut
from services.user_services import create_user

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=UserOut)
async def register_user(user_data: UserCreate, engine: AIOEngine = Depends()):
    return await create_user(engine, user_data)
