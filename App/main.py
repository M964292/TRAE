from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .auth import get_current_active_user
from .models import Student, Question, Result, AnswerRecord, TestSession
from .storage import (
    load_questions,
    save_questions,
    load_results,
    save_result,
    load_test_sessions,
    save_test_session,
    get_test_session_by_id,
    update_test_session,
    load_questions_by_level,
    save_question,
    update_question_level,
    load_student_by_name,
    save_student,
    update_student_level,
    get_storage,
    get_db
)
from App.auth import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    oauth2_scheme,
    SECRET_KEY,
    ALGORITHM,
)
from datetime import datetime

app = FastAPI(
    title="Adaptive Testing API",
    description="API для адаптивного тестирования",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение статических файлов
app.mount("/static", StaticFiles(directory="static"), name="static")

# Редирект на главную страницу для всех маршрутов
@app.get("/")
async def root():
    return FileResponse("static/index.html")

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
def save_questions_endpoint(test_name: str, data: Dict[str, Any], current_user: dict = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Сохранить вопросы теста (для учителя)"""
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        save_questions(test_name, data, db)
        return {"message": "Вопросы успешно сохранены"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/start_test")
def start_test(student: Student, test_name: str, db: Session = Depends(get_db)):
    """Начать тестирование: создать сессию ученика"""
    try:
        session = create_test_session(student, test_name)
        save_test_session(session, db)
        return session
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/next_question")
def next_question(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Получить следующий вопрос с адаптацией сложности"""
    try:
        session = get_test_session_by_id(data["session_id"], db)
        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")
        
        answer = AnswerRecord(**data)
        update_topic_stats(session, answer)
        next_level = calculate_next_level(session, answer)
        
        question = select_next_question(session)
        if not question:
            raise HTTPException(status_code=404, detail="Вопросы не найдены")
        
        return {"question": question, "next_level": next_level}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
def finish_test(data: Dict[str, Any], db: Session = Depends(get_db)):
    """Завершить тест и сохранить результат"""
    try:
        session = get_test_session_by_id(data["session_id"], db)
        if not session:
            raise HTTPException(status_code=404, detail="Сессия не найдена")
        
        result = calculate_final_stats(session)
        save_result(data["test_name"], result, db)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/teacher/results")
def get_results(data: Dict[str, Any], current_user: dict = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Получить результаты теста (для учителя)"""
    if current_user.get("role") != "teacher":
        raise HTTPException(status_code=403, detail="Доступ запрещен")
    
    try:
        results = load_results(data["test_name"], db)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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