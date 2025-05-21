from supabase import create_client
from dotenv import load_dotenv
import os

# Загружаем переменные окружения
load_dotenv()

# Получаем URL и ключ Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Создаем клиент Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Проверяем подключение
try:
    response = supabase.table("users").select("*", count="exact").execute()
    print(f"Подключение успешно! В таблице users {response.count} записей")
except Exception as e:
    print(f"Ошибка подключения: {e}")
