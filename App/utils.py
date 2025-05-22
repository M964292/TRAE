from datetime import datetime
from .models import Test, Question, AnswerRecord, TestSession

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")