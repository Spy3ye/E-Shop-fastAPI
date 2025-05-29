from odmantic import Model
from typing import Optional
from enum import Enum

class UserRole(str, Enum):
    customer = "customer"
    admin = "admin"

class User(Model):
    username: str
    email: str
    hashed_password: str
    role: UserRole = UserRole.customer
    is_active: bool = True

    class Config:
        collection = "users"
