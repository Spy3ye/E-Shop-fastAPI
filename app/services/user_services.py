# services/user_service.py
from odmantic import AIOEngine
from models.user import User
from schemas.user import UserCreate, UserOut
from fastapi import HTTPException, Depends
from utils.auth import hash_password
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def create_user(engine: AIOEngine, user_data: UserCreate) -> UserOut:
    existing = await engine.find_one(User, User.email == user_data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password)  # assume utility
    )
    await engine.save(user)
    return UserOut.model_validate(user)

async def get_current_user(token: str = Depends(oauth2_scheme), engine: AIOEngine = Depends()) -> User:
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        user = await engine.find_one(User, User.id == user_id)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except:
        raise HTTPException(status_code=401, detail="Invalid token")