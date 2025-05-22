from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import List
import json
from ..supabase_client import get_questions, add_question
from ..models.question import Question
from ..auth import get_current_user, User

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@router.post("/upload-questions", response_model=List[Question])
async def upload_questions(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Загрузка JSON файла с вопросами для учителя
    
    Args:
        file: JSON файл с вопросами
        current_user: Текущий аутентифицированный пользователь (должен быть учителем)
    
    Returns:
        List[Question]: Список загруженных вопросов
    """
    # Проверяем роль пользователя
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Только учителя могут загружать вопросы"
        )

    # Читаем файл
    try:
        contents = await file.read()
        questions_data = json.loads(contents)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Неверный формат JSON файла"
        )

    # Список для сохранения идентификаторов новых вопросов
    created_questions = []
    
    # Обрабатываем каждый вопрос
    for question_data in questions_data:
        try:
            # Добавляем обязательные поля
            question_data["created_at"] = datetime.now().isoformat()
            question_data["updated_at"] = datetime.now().isoformat()
            
            # Валидируем тип вопроса
            valid_types = ["comparison", "fractions", "geometry", "word_problem", 
                         "arithmetic", "equation", "table"]
            if question_data["type"] not in valid_types:
                raise ValueError(f"Неверный тип вопроса: {question_data['type']}")
            
            # Валидируем параметры IRT
            irt = question_data.get("irt")
            if irt:
                if not all(key in irt for key in ["model", "a", "b", "c"]):
                    raise ValueError("Неверная структура параметров IRT")
                
                # Проверяем значения параметров
                if irt["model"] != "3pl":
                    raise ValueError("Поддерживается только модель 3PL")
                if not (0 <= irt["a"] <= 5):
                    raise ValueError("Параметр a должен быть в диапазоне [0, 5]")
                if not (-5 <= irt["b"] <= 5):
                    raise ValueError("Параметр b должен быть в диапазоне [-5, 5]")
                if not (0 <= irt["c"] <= 0.3):
                    raise ValueError("Параметр c должен быть в диапазоне [0, 0.3]")
            
            # Загружаем вопрос в базу данных
            result = add_question(question_data)
            created_questions.append(result[0])
            
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Ошибка при обработке вопроса: {str(e)}"
            )
    
    return created_questions

@router.get("/download-questions", response_model=List[Question])
async def download_questions(
    current_user: User = Depends(get_current_user)
):
    """
    Получение всех вопросов для учителя
    
    Args:
        current_user: Текущий аутентифицированный пользователь (должен быть учителем)
    
    Returns:
        List[Question]: Список всех вопросов
    """
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=403,
            detail="Только учителя могут загружать вопросы"
        )
    
    questions = get_questions()
    return questions
