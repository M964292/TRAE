import psycopg2
import os
from datetime import datetime

def create_tables():
    try:
        # Подключаемся к базе данных через PostgreSQL
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host="wtycmnktsegvpduiylfq.supabase.co",
            port="5432"
        )
        
        cursor = conn.cursor()
        
        # Создаем таблицу questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                text TEXT NOT NULL,
                type TEXT NOT NULL,
                difficulty FLOAT NOT NULL,
                a_parameter FLOAT NOT NULL,
                b_parameter FLOAT NOT NULL,
                c_parameter FLOAT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Создаем таблицу test_sessions
        cursor.execute("""
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
        """)
        
        # Создаем таблицу user_answers
        cursor.execute("""
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
        """)
        
        # Создаем таблицу irt_parameters_history
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS irt_parameters_history (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                question_id UUID REFERENCES questions(id),
                a_parameter FLOAT NOT NULL,
                b_parameter FLOAT NOT NULL,
                c_parameter FLOAT NOT NULL,
                sample_size INTEGER NOT NULL,
                updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            );
        """)
        
        # Создаем индексы
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_answers_user_id ON user_answers(user_id);
            CREATE INDEX IF NOT EXISTS idx_user_answers_question_id ON user_answers(question_id);
            CREATE INDEX IF NOT EXISTS idx_test_sessions_user_id ON test_sessions(user_id);
            CREATE INDEX IF NOT EXISTS idx_questions_type ON questions(type);
            CREATE INDEX IF NOT EXISTS idx_irt_parameters_question_id ON irt_parameters_history(question_id);
        """)
        
        # Создаем политики доступа
        cursor.execute("""
            CREATE POLICY "Users can view their own data" ON users
            FOR SELECT
            USING (auth.uid() = id);
        """)
        
        cursor.execute("""
            CREATE POLICY "Teachers can view all test sessions" ON test_sessions
            FOR SELECT
            USING (auth.role() = 'teacher');
        """)
        
        cursor.execute("""
            CREATE POLICY "Students can view their own test sessions" ON test_sessions
            FOR SELECT
            USING (auth.uid() = user_id);
        """)
        
        cursor.execute("""
            CREATE POLICY "Users can insert their own answers" ON user_answers
            FOR INSERT
            WITH CHECK (auth.uid() = user_id);
        """)
        
        conn.commit()
        print("Таблицы успешно созданы!")
        
    except Exception as e:
        print(f"Ошибка при создании таблиц: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    create_tables()
