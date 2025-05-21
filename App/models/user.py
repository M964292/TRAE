from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: str  # teacher или student

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool = True

    class Config:
        from_attributes = True

class Teacher(User):
    specialization: Optional[str] = None

class Student(User):
    grade: Optional[int] = None
    class_name: Optional[str] = None
