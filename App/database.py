import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

# Получаем URL и ключ API Supabase из переменных окружения
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Создаем клиент Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Функция для выполнения запросов к Supabase
def get_supabase():
    return supabase

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
