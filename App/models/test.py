from pydantic import BaseModel
from typing import List, Optional

class Test(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    questions: List[str]  # Список ID вопросов
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True
