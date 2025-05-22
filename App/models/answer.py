from pydantic import BaseModel
from typing import Optional

class AnswerRecord(BaseModel):
    question_id: str
    given: int
    correct: bool
    difficulty: int
    score: int
