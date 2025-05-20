from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class Student(BaseModel):
    name: str
    subject_code: str
    variant_code: str
    initial_level: int = 1

class Question(BaseModel):
    id: str
    text: str
    options: List[str]
    correct_option: int  # Индекс правильного ответа (0-based)
    difficulty: int
    score: int
    topic: str
    subtopic: str

class AnswerRecord(BaseModel):
    question_id: str
    given: int  # Индекс выбранного ответа
    correct: bool
    difficulty: int
    score: int
    topic: str
    subtopic: str

class TopicStats(BaseModel):
    correct: int
    total: int
    average_difficulty: float
    success_rate: float

class TestSession(BaseModel):
    session_id: str
    student: Student
    start_time: str
    current_level: int
    questions: List[Question]
    asked: List[str]
    answers: List[AnswerRecord]
    finished: bool
    current_topic: str
    current_subtopic: str
    topic_stats: Dict[str, TopicStats]

class Result(BaseModel):
    student: str
    test_name: str
    start_time: str
    end_time: str
    answers: List[AnswerRecord]
    total_score: int
    topic_scores: Dict[str, Dict[str, Any]]  # Оценки по темам
    difficulty_distribution: Dict[int, int]  # Распределение по сложности
    time_spent: float  # Время на тест в секундах