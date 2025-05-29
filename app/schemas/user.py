from pydantic import BaseModel, EmailStr
from typing import Optional
from app.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: str
    username: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str