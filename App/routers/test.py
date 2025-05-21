from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any
from datetime import datetime
from ..models import Test, Question, AnswerRecord, TestSession
from ..database import get_supabase
from .auth import get_current_user

router = APIRouter(prefix="/tests", tags=["tests"])

@router.post("/", response_model=Dict[str, Any])
async def create_test(test: Test, current_user: Dict[str, Any] = Depends(get_current_user)):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create tests"
        )
    
    supabase = get_supabase()
    test_data = {
        "name": test.name,
        "description": test.description,
        "questions": test.questions,
        "created_by": current_user.get("id"),
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("tests").insert(test_data).execute()
    return result.data[0]

@router.get("/", response_model=List[Dict[str, Any]])
async def get_tests():
    supabase = get_supabase()
    tests = supabase.table("tests").select("*").execute()
    return tests.data

@router.get("/{test_id}", response_model=Dict[str, Any])
async def get_test(test_id: str):
    supabase = get_supabase()
    test = supabase.table("tests").select("*").eq("id", test_id).single().execute()
    if not test.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    return test.data

@router.put("/{test_id}", response_model=Dict[str, Any])
async def update_test(test_id: str, test: Test, current_user: Dict[str, Any] = Depends(get_current_user)):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can update tests"
        )
    
    supabase = get_supabase()
    test_data = {
        "name": test.name,
        "description": test.description,
        "questions": test.questions,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    result = supabase.table("tests").update(test_data).eq("id", test_id).execute()
    return result.data[0]

@router.delete("/{test_id}", response_model=Dict[str, Any])
async def delete_test(test_id: str, current_user: Dict[str, Any] = Depends(get_current_user)):
    if current_user.get("role") != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can delete tests"
        )
    
    supabase = get_supabase()
    result = supabase.table("tests").delete().eq("id", test_id).execute()
    return {"detail": "Test deleted successfully"}

@router.post("/start", response_model=Dict[str, Any])
async def start_test(student: Dict[str, Any], test_id: str):
    supabase = get_supabase()
    
    # Проверяем существование теста
    test = supabase.table("tests").select("*").eq("id", test_id).single().execute()
    if not test.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test not found"
        )
    
    # Создаем сессию тестирования
    session_data = {
        "user_id": student.get("id"),
        "session_id": str(uuid.uuid4()),
        "start_time": datetime.utcnow().isoformat(),
        "total_score": 0,
        "completed": False,
        "answers": []
    }
    
    result = supabase.table("test_sessions").insert(session_data).execute()
    return result.data[0]

@router.post("/submit", response_model=Dict[str, Any])
async def submit_answer(student: Dict[str, Any], question_id: str, answer: int):
    supabase = get_supabase()
    
    # Получаем текущую сессию
    session = supabase.table("test_sessions").select("*")\
        .eq("user_id", student.get("id")).eq("completed", False).single().execute()
    
    if not session.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Проверяем вопрос и правильность ответа
    question = supabase.table("questions").select("*")\
        .eq("id", question_id).single().execute()
    
    if not question.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Question not found"
        )
    
    is_correct = answer == question.data.get("correct_option")
    
    # Обновляем сессию с новым ответом
    answer_record = {
        "question_id": question_id,
        "given": answer,
        "correct": is_correct,
        "difficulty": question.data.get("difficulty"),
        "score": question.data.get("score")
    }
    
    session_data = session.data
    session_data["answers"].append(answer_record)
    session_data["total_score"] += question.data.get("score") if is_correct else 0
    
    result = supabase.table("test_sessions").update(session_data)\
        .eq("id", session.data.get("id")).execute()
    
    return result.data[0]

@router.post("/finish", response_model=Dict[str, Any])
async def finish_test(student: Dict[str, Any]):
    supabase = get_supabase()
    
    # Получаем текущую сессию
    session = supabase.table("test_sessions").select("*")\
        .eq("user_id", student.get("id")).eq("completed", False).single().execute()
    
    if not session.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Test session not found"
        )
    
    # Обновляем статус сессии
    session_data = session.data
    session_data["completed"] = True
    session_data["end_time"] = datetime.utcnow().isoformat()
    
    result = supabase.table("test_sessions").update(session_data)\
        .eq("id", session.data.get("id")).execute()
    
    return result.data[0]
