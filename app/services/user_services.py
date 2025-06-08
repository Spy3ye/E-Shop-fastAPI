# services/user_service.py
# from odmantic import AIOEngine
from typing import Optional
from app.models.user import User
from app.api_schemas.user import UserCreate, UserOut, UserUpdate
from fastapi import HTTPException, Depends
from app.utils.auth import hash_password , verify_password
from fastapi.security import OAuth2PasswordBearer


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

class UserServices:
    @staticmethod
    async def create_user(user: UserCreate):
        user_in = User(
            email=user.email,
            username=user.username,
            hashed_password= hash_password(user.password)
        )
        await user_in.insert()
        return user_in
    @staticmethod
    async def authenticate_user(email: str , password: str) -> Optional[User]:
        user = await User.by_email(email)
        if not user:
            return None
        if not verify_password(password=password , hashed_password = user.hashed_password):
            return None
        return user
    @staticmethod
    async def get_user_by_id(user_id):
        return await User.find_one(User.user_Id == user_id)
    @staticmethod
    async def update_user(user_id,data: UserUpdate):
        user = await User.find_one(User.user_Id == user_id)
        if not user:
            raise HTTPException(status_code=404 , detail="User not found")
        await user.update({"$set":data.dict(exclude_unset=True)})
        return user
    @staticmethod
    async def get_all_users():
        return await User.find_all().to_list()