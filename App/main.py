from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from app.models import Student, Question, Result, AnswerRecord
from app.storage import load_questions, save_questions, load_results, save_result
from app.auth import check_teacher_password
from app.utils import now_iso

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Вспомогательные структуры для сессий ---
student_sessions: Dict[str, Dict[str, Any]] = {}

# --- Эндпоинты ---

@app.get("/")
def read_root():
    return {"message": "Система тестирования работает!"}

@app.get("/tests")
def get_tests():
    """Получить список доступных тестов"""
    import os
    base = os.path.join(os.path.dirname(__file__), "..", "tests_data")
    tests = [name for name in os.listdir(base) if os.path.isdir(os.path.join(base, name))]
    return {"tests": tests}

@app.get("/questions/{test_name}")
def get_questions(test_name: str):
    """Получить все вопросы теста (для учителя)"""
    try:
        questions = load_questions(test_name)
        return {"questions": questions}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/questions/{test_name}")
def save_questions_endpoint(test_name: str, data: Dict[str, Any], password: str):
    """Сохранить вопросы теста (для учителя)"""
    if not check_teacher_password(password):
        raise HTTPException(status_code=403, detail="Неверный пароль учителя")
    questions = data.get("questions", [])
    save_questions(test_name, questions)
    return {"status": "ok"}

@app.post("/start_test")
def start_test(student: Student):
    """Начать тестирование: создать сессию ученика"""
    session_id = f"{student.name}_{student.subject_code}_{student.variant_code}_{now_iso()}"
    try:
        questions = load_questions(student.subject_code)
    except Exception as e:
        raise HTTPException(status_code=404, detail="Тест не найден")
    # Фильтруем вопросы по варианту, если нужно (можно доработать)
    session = {
        "student": student,
        "start_time": now_iso(),
        "current_level": student.initial_level,
        "questions": questions,
        "asked": [],
        "answers": [],
        "finished": False
    }
    student_sessions[session_id] = session
    return {"session_id": session_id}

@app.post("/next_question")
def next_question(data: Dict[str, Any]):
    """Получить следующий вопрос с адаптацией сложности"""
    session_id = data.get("session_id")
    if session_id not in student_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    session = student_sessions[session_id]
    if session["finished"]:
        return {"stop": True}
    level = session["current_level"]
    # Фильтруем вопросы по уровню сложности и не заданные ранее
    candidates = [q for q in session["questions"] if q["difficulty"] == level and q["id"] not in session["asked"]]
    if not candidates:
        # Если на этом уровне нет, ищем на любом уровне
        candidates = [q for q in session["questions"] if q["id"] not in session["asked"]]
    if not candidates:
        session["finished"] = True
        return {"stop": True}
    import random
    question = random.choice(candidates)
    session["asked"].append(question["id"])
    return {"stop": False, "question": question}

@app.post("/submit_answer")
def submit_answer(data: Dict[str, Any]):
    """Принять ответ ученика и адаптировать уровень сложности"""
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    answer = data.get("answer")
    if session_id not in student_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    session = student_sessions[session_id]
    question = next((q for q in session["questions"] if q["id"] == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    correct = (answer == question["answer"])
    record = {
        "question_id": question_id,
        "given": answer,
        "correct": correct,
        "difficulty": question["difficulty"],
        "score": question["score"] if correct else 0
    }
    session["answers"].append(record)
    # Адаптация уровня сложности
    if correct and question["difficulty"] < 3:
        session["current_level"] += 1
    elif not correct and question["difficulty"] > 1:
        session["current_level"] -= 1
    return {"correct": correct, "next_level": session["current_level"]}

@app.post("/finish_test")
def finish_test(data: Dict[str, Any]):
    """Завершить тест и сохранить результат"""
    session_id = data.get("session_id")
    if session_id not in student_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    session = student_sessions[session_id]
    session["finished"] = True
    total_score = sum(a["score"] for a in session["answers"])
    result = {
        "student": session["student"].name,
        "start_time": session["start_time"],
        "end_time": now_iso(),
        "answers": session["answers"],
        "total_score": total_score
    }
    save_result(session["student"].subject_code, result)
    return {"status": "ok", "total_score": total_score}

@app.post("/teacher/results")
def get_results(data: Dict[str, Any]):
    """Получить результаты теста (для учителя)"""
    test_name = data.get("test_name")
    password = data.get("password")
    if not check_teacher_password(password):
        raise HTTPException(status_code=403, detail="Неверный пароль учителя")
    results = load_results(test_name)
    return {"results": results}