from typing import List, Optional
from pydantic import BaseModel
import datetime

class Question(BaseModel):
    id: int
    text: str
    options: List[str]
    correct_answer: int
    difficulty: int  # 1-3
    points: int
    image_url: Optional[str] = None

class Test(BaseModel):
    id: str
    name: str
    description: str
    questions: List[Question]
    created_at: datetime.datetime
    updated_at: datetime.datetime

class Student(BaseModel):
    full_name: str
    test_id: str
    start_time: datetime.datetime
    end_time: Optional[datetime.datetime] = None
    current_difficulty: int
    answers: List[dict] = []  # {question_id: int, answer: int, is_correct: bool, points: int, difficulty: int}

class TestResult(BaseModel):
    student: Student
    total_points: int
    correct_answers: int
    total_questions: int
    completion_time: datetime.timedelta
