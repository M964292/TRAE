import os
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
from .models import UserCreate, User
from .database import get_supabase
from .auth import authenticate_user, create_user, create_access_token
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from .routers import test, auth as auth_router
from .database import create_tables, check_tables, create_test_user

create_tables()
check_tables()
create_test_user()

app = FastAPI(
    title="School Testing API",
    description="API для управления тестированием в школе",
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

# Настройка статических файлов и шаблонов
app.mount("/static", StaticFiles(directory="App/static"), name="static")
templates = Jinja2Templates(directory="App/templates")

# Регистрация пользователя
@app.post("/register")
async def register(user: UserCreate):
    try:
        # Создаем нового пользователя в Supabase
        user_data = {
            "email": user.email,
            "hashed_password": get_password_hash(user.password),
            "full_name": user.full_name,
            "role": user.role,
            "specialization": user.specialization,
            "grade": user.grade,
            "class_name": user.class_name,
            "is_active": True
        }
        new_user = create_user(user_data)
        
        # Создаем токен
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": new_user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Вход в систему
@app.post("/login")
async def login(user: UserCreate):
    try:
        # Аутентифицируем пользователя
        db_user = authenticate_user(user.email, user.password)
        if not db_user:
            raise HTTPException(status_code=400, detail="Incorrect email or password")
        
        # Создаем токен
        access_token = create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": db_user
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Получение информации о текущем пользователе
@app.get("/users/me")
async def read_users_me(current_user: dict = Depends(auth.get_current_user)):
    return current_user

# Получение всех пользователей (только для админов)
@app.get("/users")
async def read_users():
    try:
        supabase = get_supabase()
        response = supabase.table("users").select("*").execute()
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Получение пользователя по ID
@app.get("/users/{user_id}")
async def read_user(user_id: str):
    try:
        supabase = get_supabase()
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Обновление информации о пользователе
@app.put("/users/{user_id}")
async def update_user(user_id: str, user: UserCreate):
    try:
        supabase = get_supabase()
        user_data = {
            "email": user.email,
            "hashed_password": get_password_hash(user.password),
            "full_name": user.full_name,
            "role": user.role,
            "specialization": user.specialization,
            "grade": user.grade,
            "class_name": user.class_name,
            "is_active": True
        }
        response = supabase.table("users").update(user_data).eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return response.data[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Удаление пользователя
@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        supabase = get_supabase()
        response = supabase.table("users").delete().eq("id", user_id).execute()
        if not response.data:
            raise HTTPException(status_code=404, detail="User not found")
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return FileResponse("App/static/index.html", media_type="text/html")

@app.get("/{path:path}")
async def catch_all(path: str):
    return FileResponse("App/static/index.html", media_type="text/html")

@app.get("/tests")
async def tests_page(request: Request, current_user: dict = Depends(auth.get_current_user)):
    return templates.TemplateResponse("tests.html", {"request": request})

@app.get("/auth/login")
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/auth/register")
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Routes for teacher
@app.post("/tests")
async def create_test(test: Test):
    test_service.save_test(test)
    return {"message": "Test created successfully"}

@app.get("/tests")
async def get_tests():
    tests = []
    for file in os.listdir("tests"):
        if file.endswith(".json"):
            test = test_service.load_test(file[:-5])
            if test:
                tests.append(test)
    return tests

@app.get("/tests/{test_id}")
async def get_test(test_id: str):
    test = test_service.load_test(test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    return test

@app.put("/tests/{test_id}")
async def update_test(test_id: str, test: Test):
    test.id = test_id
    test_service.save_test(test)
    return {"message": "Test updated successfully"}

@app.delete("/tests/{test_id}")
async def delete_test(test_id: str):
    test_file = os.path.join("tests", f"{test_id}.json")
    if os.path.exists(test_file):
        os.remove(test_file)
        return {"message": "Test deleted successfully"}
    raise HTTPException(status_code=404, detail="Test not found")

@app.get("/tests/{test_id}/results")
async def get_test_results(test_id: str):
    return test_service.get_results(test_id)

# Routes for students
@app.post("/student/start")
async def start_test(student: Student):
    test = test_service.load_test(student.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    first_question = test_service.get_next_question(student)
    return {
        "test": test,
        "first_question": first_question,
        "current_difficulty": student.current_difficulty
    }

@app.post("/student/answer")
async def submit_answer(student: Student, question_id: int, answer: int):
    test = test_service.load_test(student.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    question = next((q for q in test.questions if q.id == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = question.correct_answer == answer
    student.current_difficulty = test_service.update_difficulty(student, is_correct)
    student.answers.append({
        "question_id": question_id,
        "answer": answer,
        "is_correct": is_correct,
        "points": question.points if is_correct else 0,
        "difficulty": question.difficulty
    })
    
    next_question = test_service.get_next_question(student)
    
    return {
        "next_question": next_question,
        "current_difficulty": student.current_difficulty,
        "points": question.points if is_correct else 0,
        "is_correct": is_correct
    }

@app.post("/student/finish")
async def finish_test(student: Student):
    student.end_time = datetime.now()
    test_service.save_student_result(student)
    return {"message": "Test completed successfully"}

# Routes for teacher
@app.post("/tests")
async def create_test(test: Test):
    test_service.save_test(test)
    return {"message": "Test created successfully"}
@app.get("/tests/{test_id}/questions/{difficulty}")
async def get_questions(test_id: str, difficulty: int):
    questions = test_service.get_test_questions(test_id, difficulty)
    return questions

@app.get("/")
async def root():
    return FileResponse("App/static/index.html", media_type="text/html")

@app.get("/{path:path}")
async def catch_all(path: str):
    return FileResponse("App/static/index.html", media_type="text/html")

# Routes for students
@app.post("/student/start")
async def start_test(student: Student):
    test = service.load_test(student.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    first_question = service.get_next_question(student)
    return {
        "test": test,
        "first_question": first_question,
        "current_difficulty": student.current_difficulty
    }

@app.post("/student/answer")
async def submit_answer(student: Student, question_id: int, answer: int):
    test = service.load_test(student.test_id)
    if not test:
        raise HTTPException(status_code=404, detail="Test not found")
    
    question = next((q for q in test.questions if q.id == question_id), None)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    
    is_correct = question.correct_answer == answer
    student.current_difficulty = service.update_difficulty(student, is_correct)
    student.answers.append({
        "question_id": question_id,
        "answer": answer,
        "is_correct": is_correct,
        "points": question.points if is_correct else 0,
        "difficulty": question.difficulty
    })
    
    next_question = service.get_next_question(student)
    
    return {
        "next_question": next_question,
        "current_difficulty": student.current_difficulty,
        "points": question.points if is_correct else 0,
        "is_correct": is_correct
    }

@app.post("/student/finish")
async def finish_test(student: Student):
    student.end_time = datetime.now()
    service.save_student_result(student)
    return {"message": "Test completed successfully"}

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