import os
from supabase import create_client, Client
from .models.user import UserCreate, User
from .models.test import Test
from .models.question import Question
from .models.session import TestSession
from .models.answer import AnswerRecord
from config import SUPABASE_URL, SUPABASE_KEY, TEACHER_PASSWORD_HASH, STUDENT_PASSWORD_HASH
import json
from datetime import datetime, timezone

# Создаем клиент Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Хеши паролей для тестовых пользователей
teacher_password_hash = TEACHER_PASSWORD_HASH
student_password_hash = STUDENT_PASSWORD_HASH

# Функция для выполнения запросов к Supabase
def get_supabase():
    return supabase

def create_tables():
    """Создает необходимые таблицы в Supabase"""
    client = get_supabase()
    
    # Создаем таблицу пользователей
    client.table('users').create_if_not_exists(
        columns={
            'id': 'uuid',
            'email': 'text',
            'hashed_password': 'text',
            'full_name': 'text',
            'role': 'text',
            'specialization': 'text',
            'grade': 'integer',
            'class_name': 'text',
            'is_active': 'boolean',
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    )
    
    # Создаем таблицу тестов
    client.table('tests').create_if_not_exists(
        columns={
            'id': 'uuid',
            'name': 'text',
            'description': 'text',
            'questions': 'jsonb',
            'created_by': 'text',
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    )
    
    # Создаем таблицу вопросов
    client.table('questions').create_if_not_exists(
        columns={
            'id': 'uuid',
            'text': 'text',
            'options': 'jsonb',
            'correct_option': 'integer',
            'difficulty': 'integer',
            'score': 'integer',
            'topic': 'text',
            'subtopic': 'text',
            'test_id': 'uuid'
        }
    )
    
    # Создаем таблицу результатов тестирования
    client.table('test_sessions').create_if_not_exists(
        columns={
            'id': 'uuid',
            'user_id': 'text',
            'session_id': 'text',
            'start_time': 'timestamp',
            'end_time': 'timestamp',
            'total_score': 'float',
            'completed': 'boolean',
            'answers': 'jsonb'
        }
    )
    
    print("Таблицы успешно созданы!")

def check_tables():
    """Проверяет существование таблиц в Supabase"""
    client = get_supabase()
    
    # Проверяем таблицу пользователей
    users = client.table('users').select('*').limit(1).execute()
    print(f"Таблица users: {'существует' if users.data else 'не существует'}")
    
    # Проверяем таблицу тестов
    tests = client.table('tests').select('*').limit(1).execute()
    print(f"Таблица tests: {'существует' if tests.data else 'не существует'}")
    
    # Проверяем таблицу вопросов
    questions = client.table('questions').select('*').limit(1).execute()
    print(f"Таблица questions: {'существует' if questions.data else 'не существует'}")
    
    # Проверяем таблицу результатов
    sessions = client.table('test_sessions').select('*').limit(1).execute()
    print(f"Таблица test_sessions: {'существует' if sessions.data else 'не существует'}")
    
    return users.data, tests.data, questions.data, sessions.data

def create_test_user():
    """Создает тестового пользователя в Supabase"""
    client = get_supabase()
    
    # Создаем тестового пользователя
    user_data = {
        'id': '8b6b619a-6466-4128-88ec-94abd4b3082b',
        'email': 'test@example.com',
        'hashed_password': 'testpassword',
        'full_name': 'Test User',
        'role': 'student',
        'is_active': True,
        'created_at': '2025-05-21 13:10:30.122165+00'
    }
    
    result = client.table('users').insert(user_data).execute()
    print(f"Тестовый пользователь создан: {result.data}")
    return result.data
