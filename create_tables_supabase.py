import requests
import json

# URL для Supabase API
BASE_URL = "https://wtycmnktsegvpduiylfq.supabase.co/rest/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0eWNtbmt0c2VndnBkdWl5bGZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzgyOTQ4MCwiZXhwIjoyMDYzNDA1NDgwfQ.rGchuGjDLxWyh-44TmZ81gf6QWxute_Du0WD7p-JllY"

HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_table(table_name, schema):
    url = f"{BASE_URL}/rpc/create_table"
    data = {
        "table_name": table_name,
        "schema": schema
    }
    
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        print(f"Ошибка при создании таблицы {table_name}: {response.text}")
    else:
        print(f"Таблица {table_name} успешно создана")

def create_tables():
    # Создаем таблицу questions
    questions_schema = {
        "name": "questions",
        "columns": [
            {"name": "id", "type": "uuid", "is_primary_key": True, "default": "uuid_generate_v4()"},
            {"name": "type", "type": "text", "not_null": True},
            {"name": "subject", "type": "text", "not_null": True},
            {"name": "topic", "type": "text"},
            {"name": "difficulty", "type": "text", "not_null": True},
            {"name": "text", "type": "text", "not_null": True},
            {"name": "options", "type": "jsonb"},
            {"name": "correct_answer", "type": "text", "not_null": True},
            {"name": "solution", "type": "text"},
            {"name": "irt", "type": "jsonb", "not_null": True},
            {"name": "created_at", "type": "timestamp", "default": "now()"},
            {"name": "updated_at", "type": "timestamp", "default": "now()"}
        ]
    }
    create_table("questions", questions_schema)

    # Создаем таблицу test_sessions
    test_sessions_schema = {
        "name": "test_sessions",
        "columns": [
            {"name": "id", "type": "uuid", "is_primary_key": True, "default": "uuid_generate_v4()"},
            {"name": "user_id", "type": "uuid", "not_null": True},
            {"name": "started_at", "type": "timestamp", "default": "now()"},
            {"name": "ended_at", "type": "timestamp"},
            {"name": "status", "type": "text", "not_null": True},
            {"name": "total_score", "type": "float"},
            {"name": "created_at", "type": "timestamp", "default": "now()"},
            {"name": "updated_at", "type": "timestamp", "default": "now()"}
        ]
    }
    create_table("test_sessions", test_sessions_schema)

    # Создаем таблицу user_answers
    user_answers_schema = {
        "name": "user_answers",
        "columns": [
            {"name": "id", "type": "uuid", "is_primary_key": True, "default": "uuid_generate_v4()"},
            {"name": "user_id", "type": "uuid", "not_null": True},
            {"name": "test_session_id", "type": "uuid", "not_null": True},
            {"name": "question_id", "type": "uuid", "not_null": True},
            {"name": "answer", "type": "jsonb", "not_null": True},
            {"name": "is_correct", "type": "boolean"},
            {"name": "response_time", "type": "float"},
            {"name": "created_at", "type": "timestamp", "default": "now()"}
        ]
    }
    create_table("user_answers", user_answers_schema)

    # Создаем таблицу irt_parameters_history
    irt_schema = {
        "name": "irt_parameters_history",
        "columns": [
            {"name": "id", "type": "uuid", "is_primary_key": True, "default": "uuid_generate_v4()"},
            {"name": "question_id", "type": "uuid", "not_null": True},
            {"name": "a_parameter", "type": "float", "not_null": True},
            {"name": "b_parameter", "type": "float", "not_null": True},
            {"name": "c_parameter", "type": "float", "not_null": True},
            {"name": "sample_size", "type": "integer", "not_null": True},
            {"name": "updated_at", "type": "timestamp", "default": "now()"}
        ]
    }
    create_table("irt_parameters_history", irt_schema)

if __name__ == "__main__":
    create_tables()
