from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional
from app.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    fullName: str
    email: EmailStr
    password: str
    @field_validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v

class UserOut(BaseModel):
    id: str
    username: str
    fullName: str
    email: EmailStr
    role: UserRole

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    
class UserUpdate(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    fullName: Optional[str] = None
    email: Optional[str] = None
    
class UserDelete(BaseModel):
    email: EmailStr
    password: str