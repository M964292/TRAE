from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: str  # 'student' or 'teacher'
    specialization: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None

class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    full_name: str
    role: str
    specialization: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None
    is_active: bool
    created_at: datetime

class Test(BaseModel):
    id: str
    name: str
    description: str
    questions: List[Dict[str, Any]]
    created_by: str
    created_at: datetime
    updated_at: datetime

class Question(BaseModel):
    id: str
    text: str
    options: List[str]
    correct_option: int
    difficulty: int
    score: int
    topic: str
    subtopic: str
    test_id: str

class AnswerRecord(BaseModel):
    question_id: str
    given: int
    correct: bool
    difficulty: int
    score: int
    topic: str
    subtopic: str

class TestSession(BaseModel):
    id: str
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_score: float
    completed: bool
    answers: List[AnswerRecord]

class Result(BaseModel):
    user_id: str
    test_id: str
    score: int
    total_questions: int
    correct_answers: int
    time_taken: float
    questions: List[Dict[str, Any]]  # Оценки по темам
    difficulty_distribution: Dict[int, int]  # Распределение по сложности
    time_spent: float  # Время на тест в секундах