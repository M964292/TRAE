import requests
import json
import uuid
from datetime import datetime

BASE_URL = "https://wtycmnktsegvpduiylfq.supabase.co/rest/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0eWNtbmt0c2VndnBkdWl5bGZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzgyOTQ4MCwiZXhwIjoyMDYzNDA1NDgwfQ.rGchuGjDLxWyh-44TmZ81gf6QWxute_Du0WD7p-JllY"

HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def seed_questions():
    questions = [
        {
            "id": str(uuid.uuid4()),
            "type": "arithmetic",
            "subject": "математика",
            "topic": "",
            "difficulty": "средний",
            "text": "Найдите разность 81 – 43",
            "options": [],
            "correct_answer": "38",
            "solution": "",
            "irt": {
                "model": "3pl",
                "a": 1.0,
                "b": 0.0,
                "c": 3.0
            }
        },
        {
            "id": str(uuid.uuid4()),
            "type": "comparison",
            "subject": "математика",
            "topic": "",
            "difficulty": "простой",
            "text": "Сравни числа: 25 и 37",
            "options": ["<", ">", "="],
            "correct_answer": "<",
            "solution": "",
            "irt": {
                "model": "3pl",
                "a": 0.8,
                "b": -0.5,
                "c": 2.5
            }
        },
        {
            "id": str(uuid.uuid4()),
            "type": "geometry",
            "subject": "математика",
            "topic": "прямоугольник",
            "difficulty": "средний",
            "text": "Найдите периметр прямоугольника со сторонами 5 см и 8 см",
            "options": [],
            "correct_answer": "26",
            "solution": "Периметр = 2 × (5 + 8) = 26 см",
            "irt": {
                "model": "3pl",
                "a": 1.2,
                "b": 0.3,
                "c": 2.8
            }
        }
    ]

    for question in questions:
        response = requests.post(
            f"{BASE_URL}/questions",
            headers=HEADERS,
            json=question
        )
        
        if response.status_code != 201:
            print(f"Ошибка при добавлении вопроса {question['id']}: {response.text}")
        else:
            print(f"Вопрос {question['id']} успешно добавлен")

if __name__ == "__main__":
    seed_questions()
