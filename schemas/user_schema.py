from pydantic import BaseModel
from typing import Literal

class UserCreate(BaseModel):
    email: str
    password: str
    role: Literal["admin", "user", "supplier"] = "user"  # Default role is 'user'

class UserLogin(BaseModel):
    email: str
    password: str