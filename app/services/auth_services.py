from fastapi import HTTPException
from odmantic import AIOEngine
from models.user import User
from schemas.token import Token
from schemas.user import UserLogin
from utils.auth import verify_password, create_access_token
from datetime import timedelta

async def login_user(engine: AIOEngine, credentials: UserLogin) -> Token:
    user = await engine.find_one(User, User.email == credentials.email)
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=30)
    )

    return Token(access_token=access_token)
