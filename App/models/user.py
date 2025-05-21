from sqlalchemy import Boolean, Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from App.database import Base
from enum import Enum

class UserRole(str, Enum):
    TEACHER = "teacher"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole))
    is_active = Column(Boolean, default=True)
    specialization = Column(String, nullable=True)
    grade = Column(Integer, nullable=True)
    class_name = Column(String, nullable=True)

    # Relationships
    tests = relationship("Test", back_populates="creator")
    student_results = relationship("StudentResult", back_populates="student")
