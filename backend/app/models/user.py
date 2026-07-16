from pydantic import BaseModel, EmailStr, Field
from enum import Enum
from datetime import datetime
from bson import ObjectId


class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    VIEWER = "viewer"


class UserInDB(BaseModel):
    email: EmailStr
    hashed_password: str
    full_name: str
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)