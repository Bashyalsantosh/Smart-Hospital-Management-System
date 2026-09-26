# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from uuid import UUID
from app.models.user import UserRole

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    full_name: str
    role: UserRole

class UserResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True

# app/schemas/token.py
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    user_id: str | None = None
    role: str | None = None
