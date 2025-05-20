from typing import List, Optional
from pydantic import BaseModel

class Student(BaseModel):
    name: str
    initial_level: int
    subject_code: str
    variant_code: str

class Question(BaseModel):
    id: int
    text: str
    options: List[str]
    answer: str
    difficulty: int
    score: int
    image: Optional[str] = None

class Test(BaseModel):
    name: str
    questions: List[Question]

class AnswerRecord(BaseModel):
    question_id: int
    given: str
    correct: bool
    difficulty: int
    score: int

class Result(BaseModel):
    student: str
    start_time: str
    end_time: str
    answers: List[AnswerRecord]
    total_score: int