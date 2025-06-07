from beanie import document
from uuid import UUID,uuid4
from pydantic import Field
# from odmantic import Model
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"

class User(document):
    user_Id: UUID = Field(default_factory=uuid4)
    username: str
    fullName: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.customer
    is_active: bool = True

    class Settings:
        name = "users"
