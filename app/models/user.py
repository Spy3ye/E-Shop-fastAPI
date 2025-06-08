from beanie import Document
from uuid import UUID,uuid4
from pydantic import Field,ConfigDict
# from odmantic import Model
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"

class User(Document):
    user_Id: UUID = Field(default_factory=uuid4)
    username: str
    fullName: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.customer
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)
