from pydantic import BaseModel
from typing import List, Optional

class Question(BaseModel):
    id: str
    text: str
    options: List[str]
    correct_answer: int  # Индекс правильного ответа
    difficulty: int  # Сложность от 1 до 5
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
