from fastapi import APIRouter, Depends
from odmantic import AIOEngine
from schemas.token import Token
from schemas.user import UserLogin
from services.auth_services import login_user

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, engine: AIOEngine = Depends()):
    return await login_user(engine, credentials)
