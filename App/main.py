from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any
from app.models import Student, Question, Result, AnswerRecord, TestSession
from app.storage import (
    load_questions,
    save_questions,
    load_results,
    save_result,
    create_test_session,
    update_topic_stats,
    calculate_next_level,
    select_next_question,
    calculate_final_stats
)
from app.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
)
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене заменить на конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Вспомогательные структуры для сессий ---
student_sessions: Dict[str, TestSession] = {}

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
def save_questions_endpoint(test_name: str, data: Dict[str, Any], current_user: dict = Depends(get_current_active_user)):
    """Сохранить вопросы теста (для учителя)"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Доступ только для учителей")
    questions = data.get("questions", [])
    save_questions(test_name, questions)
    return {"status": "ok"}

@app.post("/start_test")
def start_test(student: Student, test_name: str):
    """Начать тестирование: создать сессию ученика"""
    session = create_test_session(student, test_name)
    student_sessions[session.session_id] = session
    return {"session_id": session.session_id}

@app.post("/next_question")
def next_question(data: Dict[str, Any]):
    """Получить следующий вопрос с адаптацией сложности"""
    session_id = data.get("session_id")
    if session_id not in student_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    session = student_sessions[session_id]
    question = select_next_question(session)
    
    if not question:
        return {"stop": True}
    
    return {"stop": False, "question": question}

@app.post("/submit_answer")
def submit_answer(data: Dict[str, Any]):
    """Принять ответ ученика и адаптировать уровень сложности"""
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    answer_index = data.get("answer_index")
    
    if session_id not in student_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    session = student_sessions[session_id]
    question = next((q for q in session.questions if q.id == question_id), None)
    
    if not question:
        raise HTTPException(status_code=404, detail="Вопрос не найден")
    
    # Проверяем правильность ответа
    correct = (answer_index == question.correct_option)
    
    # Создаем запись ответа
    answer_record = AnswerRecord(
        question_id=question_id,
        given=answer_index,
        correct=correct,
        difficulty=question.difficulty,
        score=question.score if correct else 0,
        topic=question.topic,
        subtopic=question.subtopic
    )
    
    # Обновляем статистику по темам
    update_topic_stats(session, answer_record)
    
    # Обновляем уровень сложности
    session.current_level = calculate_next_level(session, answer_record)
    
    # Сохраняем ответ
    session.answers.append(answer_record)
    
    return {
        "correct": correct,
        "next_level": session.current_level,
        "current_topic": session.current_topic,
        "current_subtopic": session.current_subtopic
    }

@app.post("/finish_test")
def finish_test(data: Dict[str, Any]):
    """Завершить тест и сохранить результат"""
    session_id = data.get("session_id")
    if session_id not in student_sessions:
        raise HTTPException(status_code=404, detail="Сессия не найдена")
    
    session = student_sessions[session_id]
    session.finished = True
    
    # Рассчитываем финальную статистику
    stats = calculate_final_stats(session)
    
    # Формируем результат
    result = {
        "student": session.student.name,
        "test_name": session.student.subject_code,
        "start_time": session.start_time,
        "end_time": datetime.now().isoformat(),
        "answers": session.answers,
        "total_score": stats["total_score"],
        "topic_scores": stats["topic_scores"],
        "difficulty_distribution": stats["difficulty_distribution"],
        "time_spent": stats["time_spent"]
    }
    
    # Сохраняем результат
    save_result(session.student.subject_code, result)
    
    # Удаляем сессию из памяти
    del student_sessions[session_id]
    
    return {
        "status": "ok",
        "total_score": stats["total_score"],
        "topic_scores": stats["topic_scores"],
        "difficulty_distribution": stats["difficulty_distribution"],
        "time_spent": stats["time_spent"]
    }

@app.post("/teacher/results")
def get_results(data: Dict[str, Any], current_user: dict = Depends(get_current_active_user)):
    """Получить результаты теста (для учителя)"""
    if current_user["role"] != "teacher":
        raise HTTPException(status_code=403, detail="Доступ только для учителей")
    test_name = data.get("test_name")
    results = load_results(test_name)
    return {"results": results}

@app.post("/token")
async def login_for_access_token(username: str, password: str):
    user = authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_active_user)):
    return current_user

@app.get("/students/me")
async def read_student_me(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user = authenticate_user(username, "student123")
        if user is None or user["role"] != "student":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not a student",
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )