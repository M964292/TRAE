import requests
import json

BASE_URL = "https://wtycmnktsegvpduiylfq.supabase.co/rest/v1"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind0eWNtbmt0c2VndnBkdWl5bGZxIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0NzgyOTQ4MCwiZXhwIjoyMDYzNDA1NDgwfQ.rGchuGjDLxWyh-44TmZ81gf6QWxute_Du0WD7p-JllY"

HEADERS = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def execute_sql(query):
    url = f"{BASE_URL}/rpc/execute_sql"
    data = {"query": query}
    
    response = requests.post(url, headers=HEADERS, json=data)
    if response.status_code != 200:
        print(f"Ошибка при выполнении SQL: {response.text}")
    else:
        print(f"SQL успешно выполнен")

def create_tables():
    # Создаем таблицу questions
    questions_sql = """
    CREATE TABLE IF NOT EXISTS questions (
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
    """
    execute_sql(questions_sql)

    # Создаем таблицу test_sessions
    test_sessions_sql = """
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
    """
    execute_sql(test_sessions_sql)

    # Создаем таблицу user_answers
    user_answers_sql = """
    CREATE TABLE IF NOT EXISTS user_answers (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        user_id UUID REFERENCES users(id),
        test_session_id UUID REFERENCES test_sessions(id),
        question_id UUID REFERENCES questions(id),
        answer JSONB NOT NULL,
        is_correct BOOLEAN,
        response_time FLOAT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    execute_sql(user_answers_sql)

    # Создаем таблицу irt_parameters_history
    irt_history_sql = """
    CREATE TABLE IF NOT EXISTS irt_parameters_history (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        question_id UUID REFERENCES questions(id),
        a_parameter FLOAT NOT NULL,
        b_parameter FLOAT NOT NULL,
        c_parameter FLOAT NOT NULL,
        sample_size INTEGER NOT NULL,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
    );
    """
    execute_sql(irt_history_sql)

    # Создаем индексы
    indexes_sql = """
    CREATE INDEX IF NOT EXISTS idx_user_answers_user_id ON user_answers(user_id);
    CREATE INDEX IF NOT EXISTS idx_user_answers_question_id ON user_answers(question_id);
    CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions(user_id);
    CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
    CREATE INDEX IF NOT EXISTS idx_irt_parameters_question_id ON irt_parameters_history(question_id);
    """
    execute_sql(indexes_sql)

    # Создаем политики доступа
    policies_sql = """
    CREATE POLICY "Users can view their own data" ON users
    FOR SELECT
    USING (auth.uid() = id);

    CREATE POLICY "Teachers can view all test sessions" ON test_sessions
    FOR SELECT
    USING (auth.role() = 'teacher');

    CREATE POLICY "Students can view their own test sessions" ON test_sessions
    FOR SELECT
    USING (auth.uid() = user_id);

    CREATE POLICY "Users can insert their own answers" ON user_answers
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);
    """
    execute_sql(policies_sql)

if __name__ == "__main__":
    create_tables()
