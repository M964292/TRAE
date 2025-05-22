from datetime import datetime
from .models.user import UserCreate, User
from typing import Optional, List, Dict, Any

class User:
    def __init__(
        self,
        id: str,
        email: str,
        hashed_password: str,
        full_name: str,
        role: str,
        specialization: Optional[str] = None,
        grade: Optional[int] = None,
        class_name: Optional[str] = None,
        is_active: bool = True,
        created_at: datetime = datetime.utcnow()
    ):
        self.id = id
        self.email = email
        self.hashed_password = hashed_password
        self.full_name = full_name
        self.role = role
        self.specialization = specialization
        self.grade = grade
        self.class_name = class_name
        self.is_active = is_active
        self.created_at = created_at

class TestSession:
    def __init__(
        self,
        id: str,
        user_id: str,
        session_id: str,
        start_time: datetime,
        end_time: Optional[datetime] = None,
        total_score: float = 0.0,
        completed: bool = False,
        answers: Optional[List[Dict[str, Any]]] = None
    ):
        self.id = id
        self.user_id = user_id
        self.session_id = session_id
        self.start_time = start_time
        self.end_time = end_time
        self.total_score = total_score
        self.completed = completed
        self.answers = answers or []

class Question:
    def __init__(
        self,
        id: str,
        text: str,
        topic: str,
        subtopic: str,
        difficulty: int,
        score: int,
        correct_option: int
    ):
        self.id = id
        self.text = text
        self.topic = topic
        self.subtopic = subtopic
        self.difficulty = difficulty
        self.score = score
        self.correct_option = correct_option

class Answer:
    def __init__(
        self,
        id: str,
        test_session_id: str,
        question_id: str,
        given_option: int,
        is_correct: bool
    ):
        self.id = id
        self.test_session_id = test_session_id
        self.question_id = question_id
        self.given_option = given_option
        self.is_correct = is_correct
