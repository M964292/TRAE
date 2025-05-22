import requests
import json

BASE_URL = "https://wtycmnktsegvpduiylfq.supabase.co/rest/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0eWNtbmt0c2VndnBkdWl5bGZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzgyOTQ4MCwiZXhwIjoyMDYzNDA1NDgwfQ.rGchuGjDLxWyh-44TmZ81gf6QWxute_Du0WD7p-JllY"

HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_table(table_name, schema):
    # Создаем RPC функцию для создания таблицы
    create_rpc_sql = f"""
    CREATE OR REPLACE FUNCTION create_{table_name}()
    RETURNS void
    LANGUAGE plpgsql
    AS $$
    BEGIN
        CREATE TABLE IF NOT EXISTS {table_name} (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            type TEXT NOT NULL,
            subject TEXT NOT NULL,
            topic TEXT,
            difficulty TEXT NOT NULL,
            text TEXT NOT NULL,
            options JSONB,
            correct_answer TEXT NOT NULL,
            solution TEXT,
            irt JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END;
    $$;
    """
    
    # Вызываем RPC функцию
    response = requests.post(
        f"{BASE_URL}/rpc/create_{table_name}",
        headers=HEADERS,
        json={}
    )
    
    if response.status_code != 200:
        print(f"Ошибка при создании таблицы {table_name}: {response.text}")
    else:
        print(f"Таблица {table_name} успешно создана")

def create_tables():
    # Создаем таблицу questions
    create_table("questions", None)

    # Создаем таблицу test_sessions
    test_sessions_sql = """
    CREATE OR REPLACE FUNCTION create_test_sessions()
    RETURNS void
    LANGUAGE plpgsql
    AS $$
    BEGIN
        CREATE TABLE IF NOT EXISTS test_sessions (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            user_id UUID REFERENCES users(id),
            started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            ended_at TIMESTAMP WITH TIME ZONE,
            status TEXT NOT NULL,
            total_score FLOAT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    END;
    $$;
    """
    
    # Вызываем RPC функцию для test_sessions
    response = requests.post(
        f"{BASE_URL}/rpc/create_test_sessions",
        headers=HEADERS,
        json={}
    )
    
    if response.status_code != 200:
        print(f"Ошибка при создании таблицы test_sessions: {response.text}")
    else:
        print("Таблица test_sessions успешно создана")

if __name__ == "__main__":
    create_tables()
