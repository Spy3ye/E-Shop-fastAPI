from fastapi import HTTPException, UploadFile , status , Depends , APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
# from odmantic import AIOEngine
from app.models.user import User
from app.api_schemas.token import Token
from app.api_schemas.user import UserLogin
from app.services.user_services import UserServices
from app.utils.auth import verify_password, create_access_token,create_refresh_token
from datetime import timedelta

async def login_user(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    user = await UserServices.authenticate_user(
        email=form_data.email,
        password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
        
    if user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
        
    access_token = create_access_token(str(user.user_Id))
    refresh_token = create_refresh_token(str(user.user_Id))
    
    return {
        "access_token": access_token,
        "refresh_toekn": refresh_token,
        "token_type":"bearer"
    }