from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY

# Создаем клиент Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

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
