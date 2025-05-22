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
    
    # Создаем таблицу вопросов с параметрами IRT
    client.table('questions').create_if_not_exists(
        columns={
            'id': 'uuid',
            'text': 'text',
            'type': 'text',  # comparison, fractions, geometry, etc.
            'difficulty': 'float',
            'a_parameter': 'float',  # дискриминационный параметр
            'b_parameter': 'float',  # сложность
            'c_parameter': 'float',  # вероятность угадывания
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    )
    
    # Создаем таблицу сессий тестирования
    client.table('test_sessions').create_if_not_exists(
        columns={
            'id': 'uuid',
            'user_id': 'uuid',
            'started_at': 'timestamp',
            'ended_at': 'timestamp',
            'status': 'text',  # active, completed, abandoned
            'total_score': 'float',
            'created_at': 'timestamp',
            'updated_at': 'timestamp'
        }
    )
    
    # Создаем таблицу ответов пользователей
    client.table('user_answers').create_if_not_exists(
        columns={
            'id': 'uuid',
            'user_id': 'uuid',
            'test_session_id': 'uuid',
            'question_id': 'uuid',
            'answer': 'jsonb',
            'is_correct': 'boolean',
            'response_time': 'float',
            'created_at': 'timestamp'
        }
    )
    
    # Создаем таблицу истории параметров IRT
    client.table('irt_parameters_history').create_if_not_exists(
        columns={
            'id': 'uuid',
            'question_id': 'uuid',
            'a_parameter': 'float',
            'b_parameter': 'float',
            'c_parameter': 'float',
            'sample_size': 'integer',
            'updated_at': 'timestamp'
        }
    )
    
    print("Таблицы успешно созданы!")

    # Создаем индексы для оптимизации производительности
    client.query("CREATE INDEX idx_user_answers_user_id ON user_answers(user_id)")
    client.query("CREATE INDEX idx_user_answers_question_id ON user_answers(question_id)")
    client.query("CREATE INDEX idx_test_sessions_user_id ON test_sessions(user_id)")
    client.query("CREATE INDEX idx_questions_type ON questions(type)")
    client.query("CREATE INDEX idx_irt_parameters_question_id ON irt_parameters_history(question_id)")

    # Создаем политики доступа
    client.query("""
        CREATE POLICY "Users can view their own data" ON users
        FOR SELECT
        USING (auth.uid() = id);
    """)
    client.query("""
        CREATE POLICY "Teachers can view all test sessions" ON test_sessions
        FOR SELECT
        USING (auth.role() = 'teacher');
    """)
    client.query("""
        CREATE POLICY "Students can view their own test sessions" ON test_sessions
        FOR SELECT
        USING (auth.uid() = user_id);
    """)
    client.query("""
        CREATE POLICY "Users can insert their own answers" ON user_answers
        FOR INSERT
        WITH CHECK (auth.uid() = user_id);
    """)

    print("Индексы и политики успешно созданы!")

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
