import os
from supabase import create_client, Client

# URL и ключ Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

# Создаем клиент Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_questions():
    """Получение всех вопросов из Supabase"""
    return supabase.table("questions").select("*").execute().data

def add_question(question_data):
    """Добавление нового вопроса в Supabase"""
    return supabase.table("questions").insert(question_data).execute().data

def update_question(question_id, question_data):
    """Обновление вопроса в Supabase"""
    return supabase.table("questions").update(question_data).eq("id", question_id).execute().data

def delete_question(question_id):
    """Удаление вопроса из Supabase"""
    return supabase.table("questions").delete().eq("id", question_id).execute().data

def get_test_sessions(user_id=None):
    """Получение всех сессий тестирования"""
    query = supabase.table("test_sessions")
    if user_id:
        query = query.eq("user_id", user_id)
    return query.select("*").execute().data

def create_test_session(user_id, data):
    """Создание новой сессии тестирования"""
    data["user_id"] = user_id
    return supabase.table("test_sessions").insert(data).execute().data

def update_test_session(session_id, data):
    """Обновление сессии тестирования"""
    return supabase.table("test_sessions").update(data).eq("id", session_id).execute().data

def add_user_answer(user_id, test_session_id, question_id, answer_data):
    """Добавление ответа пользователя"""
    answer_data["user_id"] = user_id
    answer_data["test_session_id"] = test_session_id
    answer_data["question_id"] = question_id
    return supabase.table("user_answers").insert(answer_data).execute().data
