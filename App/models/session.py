from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TestSession(BaseModel):
    id: str
    user_id: str
    session_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    total_score: float
    completed: bool
    answers: List[dict]
